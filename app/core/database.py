from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# Khởi tạo engine bất đồng bộ với múi giờ Asia/Ho_Chi_Minh
engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
    connect_args={"server_settings": {"timezone": "Asia/Ho_Chi_Minh"}},
)

# Factory tạo phiên làm việc Database
async_session_factory = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


class Base(AsyncAttrs, DeclarativeBase):
    """Lớp cơ sở cho toàn bộ SQLAlchemy models trong hệ thống."""

    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency cung cấp AsyncSession cho mỗi request."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
