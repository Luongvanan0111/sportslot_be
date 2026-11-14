"""Cấu hình tập trung của ứng dụng.

Mọi giá trị cấu hình đọc từ biến môi trường / file `.env` qua pydantic-settings.
Import `settings` ở bất kỳ đâu để truy cập: `from app.core.config import settings`.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Cấu hình các biến môi trường hiện có của dự án."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Database ---
    database_url: str = ""

    # --- SMTP (Gửi email OTP) ---
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""

    # --- Cloudinary (Lưu trữ ảnh) ---
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""

    @property
    def DATABASE_URL(self) -> str:
        return self.database_url


@lru_cache  # Singleton: chỉ tạo một instance Settings duy nhất
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

