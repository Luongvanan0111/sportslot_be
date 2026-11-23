from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.messages import AuthMsg
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token,
    verify_password,
)
from app.models.role import RefreshToken
from app.models.user import User
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

    async def get_me(self, user: User) -> UserAuthResponse:
        """Đóng gói thông tin profile, roles và permissions của người dùng."""
        roles = await self.role_repo.get_roles_by_user_id(user.id)
        if RoleEnum.ADMIN.value in roles:
            # Nếu là Admin, đảm bảo có toàn bộ quyền trong hệ thống
            all_perms = await self.role_repo.get_all_permissions()
            permissions = [p.code for p in all_perms]
        else:
            permissions = await self.role_repo.get_permissions_by_user_id(user.id)

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

        return UserAuthResponse(
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

    async def sign_in(self, payload: SignInRequest) -> SignInResponseData:
        """Thực hiện đăng nhập bằng Email hoặc Username, bảo vệ chống brute-force."""
        now = now_vn()

        # 1. Tìm kiếm User theo Email hoặc Username
        user = await self.user_repo.get_by_identifier(payload.identifier)
        if not user:
            raise UnauthorizedError(AuthMsg.INVALID_CREDENTIALS)

        # 2. Kiểm tra trạng thái tài khoản
        if user.status == UserStatus.BANNED.value:
            raise ForbiddenError(AuthMsg.ACCOUNT_BANNED)

        # 3. Kiểm tra khóa tài khoản tạm thời
        if user.locked_until and user.locked_until > now:
            locked_time_str = user.locked_until.strftime("%Y-%m-%d %H:%M:%S")
            raise ForbiddenError(
                f"{AuthMsg.ACCOUNT_LOCKED} until {locked_time_str}"
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
                    f"{AuthMsg.ACCOUNT_LOCKED} due to too many failed attempts"
                )
            raise UnauthorizedError(AuthMsg.INVALID_CREDENTIALS)

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

        # 8. Lấy thông tin user đầy đủ
        user_auth_response = await self.get_me(user)

        return SignInResponseData(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            user=user_auth_response,
        )

    async def refresh_token(self, refresh_token_str: str) -> SignInResponseData:
        """Làm mới Access Token và Refresh Token (Refresh Token Rotation)."""
        now = now_vn()

        # 1. Giải mã và kiểm tra chữ ký token
        payload = decode_token(refresh_token_str)
        if payload.get("type") != "refresh":
            raise UnauthorizedError(AuthMsg.TOKEN_INVALID)

        sub = payload.get("sub")
        if not sub:
            raise UnauthorizedError(AuthMsg.TOKEN_INVALID)

        try:
            user_id = int(sub)
        except (ValueError, TypeError):
            raise UnauthorizedError(AuthMsg.TOKEN_INVALID)

        # 2. Tìm bản ghi Refresh Token trong DB bằng mã băm
        token_hash = hash_token(refresh_token_str)
        token_record = await self.user_repo.get_refresh_token_by_hash(token_hash)
        if not token_record or token_record.revoked_at is not None:
            raise UnauthorizedError(AuthMsg.TOKEN_INVALID)

        if token_record.expired_at < now:
            raise UnauthorizedError(AuthMsg.TOKEN_EXPIRED)

        # 3. Thu hồi token cũ (Rotation)
        await self.user_repo.revoke_refresh_token(token_record)

        # 4. Kiểm tra người dùng
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UnauthorizedError(AuthMsg.USER_NOT_FOUND)

        if user.status == UserStatus.BANNED.value:
            raise ForbiddenError(AuthMsg.ACCOUNT_BANNED)

        # 5. Sinh cặp Token mới
        token_sub = str(user.id)
        new_access_token = create_access_token(data={"sub": token_sub})
        new_refresh_token = create_refresh_token(data={"sub": token_sub})

        # 6. Lưu Refresh Token mới vào Database
        new_record = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(new_refresh_token),
            expired_at=now + timedelta(days=settings.refresh_token_expire_days),
        )
        await self.user_repo.save_refresh_token(new_record)

        # 7. Lấy thông tin user đầy đủ
        user_auth_response = await self.get_me(user)

        return SignInResponseData(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="Bearer",
            user=user_auth_response,
        )

    async def logout(self, user_id: int, refresh_token_str: str | None = None) -> None:
        """Thu hồi token khi người dùng đăng xuất."""
        if refresh_token_str:
            token_hash = hash_token(refresh_token_str)
            token_record = await self.user_repo.get_refresh_token_by_hash(token_hash)
            if token_record and token_record.user_id == user_id:
                await self.user_repo.revoke_refresh_token(token_record)
                return
        # Nếu không cung cấp refresh_token cụ thể, thu hồi toàn bộ token còn hiệu lực của user
        await self.user_repo.revoke_user_refresh_tokens(user_id)
