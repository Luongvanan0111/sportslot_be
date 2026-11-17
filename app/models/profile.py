from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import AuditMixin, BigIntPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User


class Profile(Base, BigIntPrimaryKeyMixin, AuditMixin):
    """Bảng hồ sơ cá nhân người dùng, liên kết 1-1 với bảng users."""

    __tablename__ = "profile"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    full_name: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    full_name_no_uni: Mapped[str | None] = mapped_column(
        Text,
        index=True,
        nullable=True,
    )
    phone: Mapped[str | None] = mapped_column(
        Text,
        index=True,
        nullable=True,
    )
    bio: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    dob: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )
    gender: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )
    province_code: Mapped[str | None] = mapped_column(
        Text,
        index=True,
        nullable=True,
    )
    province_name: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    district_code: Mapped[str | None] = mapped_column(
        Text,
        index=True,
        nullable=True,
    )
    district_name: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    ward_code: Mapped[str | None] = mapped_column(
        Text,
        index=True,
        nullable=True,
    )
    ward_name: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    street_address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    avatar_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Quan hệ ngược 1-1 với User
    user: Mapped["User"] = relationship(
        "User",
        back_populates="profile",
    )
