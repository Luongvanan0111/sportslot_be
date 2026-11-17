from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import (
    Permission,
    Role,
    RolePermission,
    UserRole,
)


class RoleRepository:
    """Tầng truy vấn dữ liệu cho các thực thể Role, Permission và quan hệ RBAC."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_name(self, name: str) -> Role | None:
        """Tìm vai trò theo tên."""
        stmt = select(Role).where(Role.name == name, Role.delete_flag.is_(False))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_permission_by_code(self, code: str) -> Permission | None:
        """Tìm quyền theo mã code."""
        stmt = select(Permission).where(
            Permission.code == code, Permission.delete_flag.is_(False)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_roles_by_user_id(self, user_id: int) -> list[str]:
        """Lấy danh sách tên vai trò của một người dùng."""
        stmt = (
            select(Role.name)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id, Role.delete_flag.is_(False))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_permissions_by_user_id(self, user_id: int) -> list[str]:
        """Lấy danh sách mã quyền duy nhất (distinct) của một người dùng thông qua các vai trò."""
        stmt = (
            select(Permission.code)
            .distinct()
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(UserRole, UserRole.role_id == RolePermission.role_id)
            .join(Role, Role.id == UserRole.role_id)
            .where(
                UserRole.user_id == user_id,
                Role.delete_flag.is_(False),
                Permission.delete_flag.is_(False),
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_all_permissions(self) -> list[Permission]:
        """Lấy danh sách tất cả quyền trong hệ thống."""
        stmt = select(Permission).where(Permission.delete_flag.is_(False))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_role(self, name: str, description: str | None = None) -> Role:
        """Tạo vai trò mới."""
        role = Role(name=name, description=description)
        self.db.add(role)
        await self.db.flush()
        await self.db.refresh(role)
        return role

    async def create_permission(
        self, code: str, description: str | None = None
    ) -> Permission:
        """Tạo quyền kỹ thuật mới."""
        permission = Permission(code=code, description=description)
        self.db.add(permission)
        await self.db.flush()
        await self.db.refresh(permission)
        return permission

    async def assign_permission_to_role(
        self, role_id: int, permission_id: int
    ) -> RolePermission | None:
        """Gán quyền cho một vai trò (nếu chưa gán)."""
        stmt = select(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id,
        )
        existing = (await self.db.execute(stmt)).scalar_one_or_none()
        if not existing:
            assoc = RolePermission(role_id=role_id, permission_id=permission_id)
            self.db.add(assoc)
            await self.db.flush()
            return assoc
        return existing

    async def assign_role_to_user(
        self, user_id: int, role_id: int
    ) -> UserRole | None:
        """Gán vai trò cho người dùng (nếu chưa gán)."""
        stmt = select(UserRole).where(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id,
        )
        existing = (await self.db.execute(stmt)).scalar_one_or_none()
        if not existing:
            assoc = UserRole(user_id=user_id, role_id=role_id)
            self.db.add(assoc)
            await self.db.flush()
            return assoc
        return existing
