from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import AuditMixin, BigIntPrimaryKeyMixin
from app.utils.enums import UserStatus

if TYPE_CHECKING:
    from app.models.profile import Profile
    from app.models.role import RefreshToken, Role
    from app.models.term import UserTermAcceptance


class User(Base, BigIntPrimaryKeyMixin, AuditMixin):
    """Bảng tài khoản người dùng đăng nhập hệ thống."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        Text,
        unique=True,
        index=True,
        nullable=False,
    )
    username: Mapped[str] = mapped_column(
        Text,
        unique=True,
        index=True,
        nullable=False,
    )
    password_hash: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    google_id: Mapped[str | None] = mapped_column(
        Text,
        unique=True,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=UserStatus.UNVERIFIED.value,
        server_default=UserStatus.UNVERIFIED.value,
        nullable=False,
    )
    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    failed_login_attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
    )
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Quan hệ 1-1 với Profile
    profile: Mapped["Profile"] = relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Quan hệ Nhiều-Nhiều với Role thông qua user_roles
    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users",
        lazy="selectin",
    )

    # Quan hệ 1-N với RefreshToken
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # Quan hệ 1-N với UserTermAcceptance
    term_acceptances: Mapped[list["UserTermAcceptance"]] = relationship(
        "UserTermAcceptance",
        back_populates="user",
        cascade="all, delete-orphan",
    )
