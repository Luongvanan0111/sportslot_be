from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Identity, Text, func
from sqlalchemy.orm import Mapped, mapped_column


class BigIntPrimaryKeyMixin:
    """Mixin cung cấp khóa chính BigInteger tự tăng với Identity(always=False)."""

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=False),
        primary_key=True,
    )


class AuditMixin:
    """Mixin cung cấp 5 trường kiểm toán dữ liệu (Audit fields) bắt buộc."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    created_by: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    updated_by: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    delete_flag: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        index=True,
        nullable=False,
    )
