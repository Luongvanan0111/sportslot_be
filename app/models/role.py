from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import AuditMixin, BigIntPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User


class UserRole(Base):
    """Bảng nối quan hệ Nhiều-Nhiều giữa Người dùng và Vai trò."""

    __tablename__ = "user_roles"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class RolePermission(Base):
    """Bảng nối quan hệ Nhiều-Nhiều giữa Vai trò và Quyền hạn kỹ thuật."""

    __tablename__ = "role_permissions"

    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class Role(Base, BigIntPrimaryKeyMixin, AuditMixin):
    """Bảng danh mục các vai trò trong hệ thống (admin, owner, user)."""

    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(
        Text,
        unique=True,
        index=True,
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Quan hệ Nhiều-Nhiều với User
    users: Mapped[list["User"]] = relationship(
        "User",
        secondary="user_roles",
        back_populates="roles",
    )

    # Quan hệ Nhiều-Nhiều với Permission
    permissions: Mapped[list["Permission"]] = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles",
        lazy="selectin",
    )


class Permission(Base, BigIntPrimaryKeyMixin, AuditMixin):
    """Bảng lưu trữ danh mục quyền hạn kỹ thuật theo chuẩn resource:action."""

    __tablename__ = "permissions"

    code: Mapped[str] = mapped_column(
        Text,
        unique=True,
        index=True,
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Quan hệ Nhiều-Nhiều với Role
    roles: Mapped[list[Role]] = relationship(
        Role,
        secondary="role_permissions",
        back_populates="permissions",
    )


class RefreshToken(Base, BigIntPrimaryKeyMixin):
    """Bảng lưu trữ thông tin băm của Refresh Token phục vụ thu hồi và rotation."""

    __tablename__ = "refresh_tokens"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(
        Text,
        unique=True,
        index=True,
        nullable=False,
    )
    expired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        nullable=False,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Quan hệ với User
    user: Mapped["User"] = relationship(
        "User",
        back_populates="refresh_tokens",
    )
