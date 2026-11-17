from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Chuẩn envelope phản hồi API thống nhất toàn hệ thống."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    success: bool = True
    status_code: int = 200
    message: str = "Success"
    data: T | None = None


def ok(
    data: T | None = None,
    message: str = "Success",
    status_code: int = 200,
) -> ApiResponse[T]:
    """Helper bọc dữ liệu thành ApiResponse thành công."""
    return ApiResponse(
        success=True,
        status_code=status_code,
        message=message,
        data=data,
    )


class Page(BaseModel, Generic[T]):
    """DTO phân trang chuẩn cho các danh sách."""

    items: list[T]
    total: int
    page: int
    size: int
    total_pages: int

    @classmethod
    def create(cls, items: list[T], total: int, page: int, size: int) -> "Page[T]":
        total_pages = (total + size - 1) // size if size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            total_pages=total_pages,
        )
