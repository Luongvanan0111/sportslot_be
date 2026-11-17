from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import AuditMixin, BigIntPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User


class Term(Base, BigIntPrimaryKeyMixin, AuditMixin):
    """Bảng lưu trữ các phiên bản Điều khoản dịch vụ và Chính sách."""

    __tablename__ = "terms"

    version: Mapped[str] = mapped_column(
        Text,
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    title_no_uni: Mapped[str | None] = mapped_column(
        Text,
        index=True,
        nullable=True,
    )
    content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    effective_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        nullable=False,
    )

    # Lịch sử chấp thuận điều khoản của người dùng
    acceptances: Mapped[list["UserTermAcceptance"]] = relationship(
        "UserTermAcceptance",
        back_populates="term",
        cascade="all, delete-orphan",
    )


class UserTermAcceptance(Base):
    """Bảng lưu vết kiểm toán việc chấp thuận điều khoản của người dùng."""

    __tablename__ = "user_terms_acceptances"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    term_id: Mapped[int] = mapped_column(
        ForeignKey("terms.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    accepted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Quan hệ với User và Term
    user: Mapped["User"] = relationship(
        "User",
        back_populates="term_acceptances",
    )
    term: Mapped[Term] = relationship(
        Term,
        back_populates="acceptances",
    )
