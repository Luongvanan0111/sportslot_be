"""Cấu hình tập trung của ứng dụng.

Mọi giá trị cấu hình được đọc tự động từ biến môi trường / file `.env` qua pydantic-settings.
Import `settings` ở bất kỳ đâu để truy cập: `from app.core.config import settings`.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Định vị đường dẫn tuyệt đối tới file .env ở thư mục gốc của dự án
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Cấu hình các biến môi trường của dự án (100% nạp từ file .env)."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Ứng dụng ---
    app_name: str = "SportSlot Backend API"

    # --- Database ---
    database_url: str = ""

    # --- Security & JWT ---
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    refresh_token_expire_days: int = 30
    otp_secret_key: str = ""

    # --- Brute-force & Khóa tài khoản ---
    max_failed_login_attempts: int = 5
    account_lock_minutes: int = 15

    # --- Tài khoản Admin Mặc định & Profile (Seed lúc khởi động) ---
    admin_email: str = ""
    admin_password: str = ""
    admin_username: str = ""
    admin_full_name: str = ""

    # --- SMTP (Gửi email OTP) ---
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""

    # --- Cloudinary (Lưu trữ ảnh) ---
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""

    # --- CORS ---
    cors_origins: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        """Tách chuỗi các domain CORS thành danh sách list."""
        default_origins = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://localhost:3000",
        ]
        if not self.cors_origins:
            return default_origins
        configured = [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]
        for o in default_origins:
            if o not in configured:
                configured.append(o)
        return configured

    @property
    def DATABASE_URL(self) -> str:
        """Tương thích với alembic/env.py."""
        return self.database_url


@lru_cache  # Singleton: chỉ tạo một instance Settings duy nhất
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
