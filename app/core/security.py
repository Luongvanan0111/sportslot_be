from datetime import timedelta
import hashlib
from typing import Any

import jwt
from pwdlib import PasswordHash

from app.core.config import settings
from app.core.exceptions import UnauthorizedError
from app.utils.timezone import now_vn

# Quản lý băm mật khẩu với thuật toán Argon2id chuẩn hóa
password_hash_helper = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Băm mật khẩu bằng thuật toán Argon2id."""
    return password_hash_helper.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiểm tra mật khẩu nhập vào khớp với chuỗi băm hay không."""
    return password_hash_helper.verify(plain_password, hashed_password)


def create_token(
    data: dict[str, Any],
    expires_delta: timedelta,
    token_type: str = "access",
) -> str:
    """Tạo JWT token có thời hạn và loại token cụ thể."""
    to_encode = data.copy()
    now = now_vn()
    expire = now + expires_delta
    to_encode.update(
        {
            "exp": expire,
            "iat": now,
            "type": token_type,
        }
    )
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """Tạo Access Token."""
    delta = expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    return create_token(data, delta, token_type="access")


def create_refresh_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """Tạo Refresh Token."""
    delta = expires_delta or timedelta(days=settings.refresh_token_expire_days)
    return create_token(data, delta, token_type="refresh")


def decode_token(token: str) -> dict[str, Any]:
    """Giải mã và xác thực chữ ký JWT token."""
    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Token has expired")
    except jwt.InvalidTokenError:
        raise UnauthorizedError("Invalid token")


def hash_token(token: str) -> str:
    """Băm chuỗi token bằng SHA-256 để lưu trữ an toàn trong database."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
