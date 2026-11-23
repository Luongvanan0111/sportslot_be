from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.messages import AuthMsg
from app.core.security import decode_token
from app.models.user import User
from app.repositories.role_repo import RoleRepository
from app.repositories.user_repo import UserRepository
from app.utils.enums import UserStatus

# Cung cấp dependency phiên làm việc cơ sở dữ liệu
DbSession = Annotated[AsyncSession, Depends(get_db)]

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/sign-in",
    auto_error=False,
)


async def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: DbSession,
) -> User:
    """Dependency xác thực JWT Bearer Token và trả về thông tin User hiện tại."""
    if not token:
        raise UnauthorizedError(AuthMsg.NOT_AUTHENTICATED)

    payload = decode_token(token)
    if payload.get("type") != "access":
        raise UnauthorizedError("Invalid token type")

    sub = payload.get("sub")
    if not sub:
        raise UnauthorizedError("Invalid token subject")

    try:
        user_id = int(sub)
    except (ValueError, TypeError):
        raise UnauthorizedError("Invalid token user identifier")

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UnauthorizedError(AuthMsg.USER_NOT_FOUND)

    if user.status == UserStatus.BANNED.value:
        raise ForbiddenError(AuthMsg.ACCOUNT_BANNED)

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_permission(permission_code: str) -> Callable:
    """Dependency factory kiểm tra người dùng có quyền thực thi thao tác cụ thể hay không."""

    async def dependency(
        current_user: CurrentUser,
        db: DbSession,
    ) -> User:
        user_role_names = [role.name for role in current_user.roles]

        # Quản trị viên (admin) mặc định sở hữu toàn bộ quyền trong hệ thống
        if "admin" in user_role_names:
            return current_user

        role_repo = RoleRepository(db)
        user_permissions = await role_repo.get_permissions_by_user_id(current_user.id)
        if permission_code not in user_permissions:
            raise ForbiddenError(f"Permission denied: require '{permission_code}'")

        return current_user

    return dependency
