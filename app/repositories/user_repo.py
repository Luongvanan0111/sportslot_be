from datetime import timedelta

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import RefreshToken
from app.models.user import User
from app.utils.timezone import now_vn


class UserRepository:
    """Tầng truy vấn dữ liệu cho thực thể User và RefreshToken."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        """Tìm người dùng theo ID (chỉ lấy tài khoản chưa bị xóa mềm)."""
        stmt = select(User).where(User.id == user_id, User.delete_flag.is_(False))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_identifier(self, identifier: str) -> User | None:
        """Tìm người dùng theo Email hoặc Username (không phân biệt hoa thường)."""
        clean_id = identifier.strip().lower()
        stmt = select(User).where(
            or_(
                func.lower(User.email) == clean_id,
                func.lower(User.username) == clean_id,
            ),
            User.delete_flag.is_(False),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Tìm người dùng theo Email."""
        clean_email = email.strip().lower()
        stmt = select(User).where(
            func.lower(User.email) == clean_email,
            User.delete_flag.is_(False),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """Tìm người dùng theo Username."""
        clean_username = username.strip().lower()
        stmt = select(User).where(
            func.lower(User.username) == clean_username,
            User.delete_flag.is_(False),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        """Tạo mới một User vào phiên làm việc (sử dụng flush)."""
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def increment_failed_attempts(
        self, user: User, max_attempts: int, lock_minutes: int
    ) -> User:
        """Tăng số lần đăng nhập thất bại. Nếu vượt quá max_attempts, khóa tài khoản."""
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= max_attempts:
            user.locked_until = now_vn() + timedelta(minutes=lock_minutes)
        await self.db.flush()
        return user

    async def reset_failed_attempts(self, user: User) -> User:
        """Đặt lại số lần đăng nhập thất bại, gỡ khóa và cập nhật last_login_at."""
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = now_vn()
        await self.db.flush()
        return user

    async def save_refresh_token(self, refresh_token: RefreshToken) -> RefreshToken:
        """Lưu trữ chuỗi băm của Refresh Token."""
        self.db.add(refresh_token)
        await self.db.flush()
        return refresh_token

    async def get_refresh_token_by_hash(self, token_hash: str) -> RefreshToken | None:
        """Tìm kiếm RefreshToken theo chuỗi băm."""
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke_refresh_token(self, token_record: RefreshToken) -> None:
        """Thu hồi một RefreshToken bằng cách gán thời điểm revoked_at."""
        token_record.revoked_at = now_vn()
        await self.db.flush()

    async def revoke_user_refresh_tokens(self, user_id: int) -> None:
        """Thu hồi toàn bộ RefreshToken còn hiệu lực của người dùng."""
        stmt = select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )
        result = await self.db.execute(stmt)
        tokens = result.scalars().all()
        now = now_vn()
        for t in tokens:
            t.revoked_at = now
        await self.db.flush()
