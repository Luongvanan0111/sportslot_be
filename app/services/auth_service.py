from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_token,
    verify_password,
)
from app.models.role import RefreshToken
from app.repositories.role_repo import RoleRepository
from app.repositories.user_repo import UserRepository
from app.schemas.auth import (
    SignInRequest,
    SignInResponseData,
    UserAuthResponse,
    UserProfileResponse,
)
from app.utils.enums import RoleEnum, UserStatus
from app.utils.timezone import now_vn


class AuthService:
    """Tầng xử lý logic nghiệp vụ cho xác thực người dùng (Authentication)."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)

    async def sign_in(self, payload: SignInRequest) -> SignInResponseData:
        """Thực hiện đăng nhập bằng Email hoặc Username, bảo vệ chống brute-force."""
        now = now_vn()

        # 1. Tìm kiếm User theo Email hoặc Username
        user = await self.user_repo.get_by_identifier(payload.identifier)
        if not user:
            raise UnauthorizedError("Invalid credentials")

        # 2. Kiểm tra trạng thái tài khoản
        if user.status == UserStatus.BANNED.value:
            raise ForbiddenError("Account has been banned")

        # 3. Kiểm tra khóa tài khoản tạm thời
        if user.locked_until and user.locked_until > now:
            locked_time_str = user.locked_until.strftime("%Y-%m-%d %H:%M:%S")
            raise ForbiddenError(
                f"Account is temporarily locked until {locked_time_str}"
            )

        # 4. Kiểm tra mật khẩu băm Argon2
        if not user.password_hash or not verify_password(
            payload.password, user.password_hash
        ):
            # Tăng số lần thử sai
            await self.user_repo.increment_failed_attempts(
                user,
                max_attempts=settings.max_failed_login_attempts,
                lock_minutes=settings.account_lock_minutes,
            )
            if user.locked_until and user.locked_until > now:
                raise ForbiddenError(
                    "Account locked due to too many failed attempts"
                )
            raise UnauthorizedError("Invalid credentials")

        # 5. Đăng nhập thành công: reset bộ đếm sai & cập nhật thời điểm đăng nhập
        await self.user_repo.reset_failed_attempts(user)

        # 6. Sinh cặp Access Token và Refresh Token
        token_sub = str(user.id)
        access_token = create_access_token(data={"sub": token_sub})
        refresh_token = create_refresh_token(data={"sub": token_sub})

        # 7. Lưu bản ghi Refresh Token (dạng băm SHA-256) vào Database
        refresh_record = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(refresh_token),
            expired_at=now + timedelta(days=settings.refresh_token_expire_days),
        )
        await self.user_repo.save_refresh_token(refresh_record)

        # 8. Lấy danh sách Roles & Permissions
        roles = await self.role_repo.get_roles_by_user_id(user.id)
        if RoleEnum.ADMIN.value in roles:
            # Nếu là Admin, đảm bảo có toàn bộ quyền trong hệ thống
            all_perms = await self.role_repo.get_all_permissions()
            permissions = [p.code for p in all_perms]
        else:
            permissions = await self.role_repo.get_permissions_by_user_id(user.id)

        # 9. Đóng gói thông tin Profile nếu có
        profile_data = None
        if user.profile:
            profile_data = UserProfileResponse(
                full_name=user.profile.full_name,
                avatar_url=user.profile.avatar_url,
                phone_number=user.profile.phone,
                gender=user.profile.gender,
                date_of_birth=user.profile.dob,
                address=user.profile.street_address,
            )

        user_auth_response = UserAuthResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            status=user.status,
            verified_at=user.verified_at,
            last_login_at=user.last_login_at,
            profile=profile_data,
            roles=roles,
            permissions=permissions,
        )

        return SignInResponseData(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user_auth_response,
        )
