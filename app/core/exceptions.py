from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.logging import logger


class AppError(Exception):
    """Lớp cơ sở cho toàn bộ ngoại lệ nghiệp vụ trong ứng dụng (100% tiếng Anh)."""

    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = 400,
        error_code: str = "BAD_REQUEST",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}


class NotFoundError(AppError):
    def __init__(
        self,
        message: str = "Resource not found",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            details=details,
        )


class UnauthorizedError(AppError):
    def __init__(
        self,
        message: str = "Unauthorized",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=401,
            error_code="UNAUTHORIZED",
            details=details,
        )


class ForbiddenError(AppError):
    def __init__(
        self,
        message: str = "Forbidden",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=403,
            error_code="FORBIDDEN",
            details=details,
        )


class ConflictError(AppError):
    def __init__(
        self,
        message: str = "Conflict detected",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT",
            details=details,
        )


class BadRequestError(AppError):
    def __init__(
        self,
        message: str = "Bad request",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=400,
            error_code="BAD_REQUEST",
            details=details,
        )


def register_exception_handlers(app: FastAPI) -> None:
    """Đăng ký các bộ xử lý lỗi thống nhất cho FastAPI app."""

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        logger.warning(
            f"[AppError] {request.method} {request.url.path} - "
            f"Status: {exc.status_code} - Code: {exc.error_code} - Message: {exc.message}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "status_code": exc.status_code,
                "message": exc.message,
                "data": None,
                "error_code": exc.error_code,
                "details": exc.details,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.warning(
            f"[ValidationError] {request.method} {request.url.path} - Details: {exc.errors()}"
        )
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "status_code": 422,
                "message": "Validation error",
                "data": None,
                "error_code": "VALIDATION_ERROR",
                "details": {"errors": exc.errors()},
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.error(
            f"[UnhandledException] {request.method} {request.url.path}: {exc}",
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "status_code": 500,
                "message": "Internal server error",
                "data": None,
                "error_code": "INTERNAL_SERVER_ERROR",
                "details": {},
            },
        )
