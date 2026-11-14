import asyncio
from contextlib import asynccontextmanager
import smtplib
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings

try:
    import cloudinary
    import cloudinary.api
    HAS_CLOUDINARY = True
except ImportError:
    HAS_CLOUDINARY = False


async def check_database() -> str:
    """Kiểm tra kết nối Database bằng lệnh SELECT 1."""
    if not settings.database_url:
        return "not_configured"
    try:
        engine = create_async_engine(settings.database_url)
        async with asyncio.timeout(5):
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
        await engine.dispose()
        return "connected"
    except Exception as e:
        return f"disconnected: {e}"


def check_smtp_sync() -> str:
    """Kiểm tra bắt tay và xác thực với SMTP Server."""
    host = settings.smtp_host
    port = settings.smtp_port
    user = settings.smtp_user
    pwd = settings.smtp_password
    if not (host and user and pwd):
        return "not_configured"
    try:
        server = smtplib.SMTP(host, port, timeout=5)
        server.starttls()
        server.login(user, pwd)
        server.quit()
        return "connected"
    except Exception as e:
        return f"disconnected: {e}"


def check_cloudinary_sync() -> str:
    """Kiểm tra API Key & Secret qua Cloudinary ping."""
    if not HAS_CLOUDINARY:
        return "not_installed (run: uv add cloudinary)"
    c_name = settings.cloudinary_cloud_name
    c_key = settings.cloudinary_api_key
    c_sec = settings.cloudinary_api_secret
    if not (c_name and c_key and c_sec):
        return "not_configured"
    try:
        cloudinary.config(
            cloud_name=c_name,
            api_key=c_key,
            api_secret=c_sec,
            secure=True,
        )
        res = cloudinary.api.ping()
        return "connected" if res.get("status") == "ok" else f"disconnected: {res}"
    except Exception as e:
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n" + "=" * 50)
    print("[STARTUP] Đang kiểm tra kết nối dịch vụ...")
    print("=" * 50)

    services_status = await check_all_services()
    app.state.services_status = services_status

    for svc, status in services_status.items():
        icon = "✅" if status == "connected" else "❌"
        print(f"  {icon} [{svc.capitalize()}] {status}")

    print("=" * 50 + "\n")
    yield


app = FastAPI(
    title="SportSlot Backend API",
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan,
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["Healthcheck"])
async def health_check(live: bool = False) -> dict[str, Any]:
    """Endpoint kiểm tra trạng thái hoạt động của server và các dịch vụ.
    - Mặc định: trả về kết quả lưu từ lúc khởi động server.
    - live=true: thực hiện kiểm tra trực tiếp lại các dịch vụ.
    """
    services = await check_all_services() if live else getattr(app.state, "services_status", {})
    return {
        "server": "SportSlot Backend API",
        "message": "Server is running",
        "version": "1.0.0",
        "services": services,
    }
