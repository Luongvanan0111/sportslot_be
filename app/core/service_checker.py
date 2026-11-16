import asyncio
import smtplib

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.core.logging import logger

try:
    import cloudinary
    import cloudinary.api
    import cloudinary.exceptions

    HAS_CLOUDINARY = True
except ImportError:
    HAS_CLOUDINARY = False


async def check_database() -> str:
    """Kiểm tra kết nối Database bằng lệnh SELECT 1."""
    if not settings.database_url:
        logger.warning("  [Database] not_configured")
        return "not_configured"
    try:
        engine = create_async_engine(settings.database_url)
        async with asyncio.timeout(5):
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
        await engine.dispose()
        logger.info("  [Database] connected")
        return "connected"
    except (SQLAlchemyError, TimeoutError, OSError) as e:
        logger.error(f"  [Database] disconnected: {e}")
        return f"disconnected: {e}"


def check_smtp_sync() -> str:
    """Kiểm tra bắt tay và xác thực với SMTP Server."""
    host = settings.smtp_host
    port = settings.smtp_port
    user = settings.smtp_user
    pwd = settings.smtp_password
    if not (host and user and pwd):
        logger.warning("  [Smtp] not_configured")
        return "not_configured"
    try:
        server = smtplib.SMTP(host, port, timeout=5)
        server.starttls()
        server.login(user, pwd)
        server.quit()
        logger.info("  [Smtp] connected")
        return "connected"
    except (smtplib.SMTPException, TimeoutError, OSError) as e:
        logger.error(f"  [Smtp] disconnected: {e}")
        return f"disconnected: {e}"


def check_cloudinary_sync() -> str:
    """Kiểm tra API Key & Secret qua Cloudinary ping."""
    if not HAS_CLOUDINARY:
        logger.warning("  [Cloudinary] not_installed (run: uv add cloudinary)")
        return "not_installed (run: uv add cloudinary)"
    c_name = settings.cloudinary_cloud_name
    c_key = settings.cloudinary_api_key
    c_sec = settings.cloudinary_api_secret
    if not (c_name and c_key and c_sec):
        logger.warning("  [Cloudinary] not_configured")
        return "not_configured"
    try:
        cloudinary.config(
            cloud_name=c_name,
            api_key=c_key,
            api_secret=c_sec,
            secure=True,
        )
        res = cloudinary.api.ping()
        if res.get("status") == "ok":
            logger.info("  [Cloudinary] connected")
            return "connected"
        else:
            logger.error(f"  [Cloudinary] disconnected: {res}")
            return f"disconnected: {res}"
    except (cloudinary.exceptions.Error, TimeoutError, OSError) as e:
        logger.error(f"  [Cloudinary] disconnected: {e}")
        return f"disconnected: {e}"


async def check_all_services() -> dict[str, str]:
    """Kiểm tra đồng thời cả 3 dịch vụ."""
    db_status, smtp_status, cloudinary_status = await asyncio.gather(
        check_database(),
        asyncio.to_thread(check_smtp_sync),
        asyncio.to_thread(check_cloudinary_sync),
    )
    return {
        "database": db_status,
        "smtp": smtp_status,
        "cloudinary": cloudinary_status,
    }
