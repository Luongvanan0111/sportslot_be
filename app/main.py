from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.core.logging import init_logger_file, logger
from app.core.middlewares import log_requests_middleware
from app.core.service_checker import check_all_services


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi tạo file log timestamp cho phiên chạy này
    log_file = init_logger_file()

    logger.info("=" * 50)
    logger.info("[STARTUP] Đang kiểm tra kết nối dịch vụ...")
    logger.info(f"[LOG FILE] logs/{log_file.name}")
    logger.info("=" * 50)

    services_status = await check_all_services()
    app.state.services_status = services_status

    logger.info("=" * 50)
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan,
)

# Đăng ký middleware ghi log request/response
app.middleware("http")(log_requests_middleware)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["Healthcheck"])
async def health_check() -> dict[str, Any]:
    """Endpoint kiểm tra trạng thái hoạt động của server và các dịch vụ."""
    logger.info("[HEALTHCHECK] Kiểm tra trạng thái server và dịch vụ...")
    return {
        "server": settings.app_name,
        "message": "Server is running",
        "version": "1.0.0",
        "services": getattr(app.state, "services_status", {}),
    }
