
import http

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

app = FastAPI(
    title="SportSlot Backend API",
    version="1.0.0",
    docs_url="/docs",
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Thay đổi thành URL của frontend của bạn
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")

@app.get("/health", tags=["Healthcheck"])
async def health_check() -> dict[str, str | bool]:
    """Endpoint kiểm tra trạng thái hoạt động của server."""
    return {
        "server": "SportSlot Backend API",
        "message": "Server is running",
        "version": "1.0.0",
    }