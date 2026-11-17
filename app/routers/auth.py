from fastapi import APIRouter, status

from app.core.deps import DbSession
from app.schemas.auth import SignInRequest, SignInResponseData
from app.schemas.response import ApiResponse, ok
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post(
    "/sign-in",
    response_model=ApiResponse[SignInResponseData],
    status_code=status.HTTP_200_OK,
    summary="Đăng nhập tài khoản bằng Email hoặc Username",
    description="Xác thực thông tin người dùng, kiểm tra khóa tài khoản, trả về JWT Access Token, Refresh Token và thông tin phân quyền.",
)
async def sign_in(
    payload: SignInRequest,
    db: DbSession,
) -> ApiResponse[SignInResponseData]:
    """Endpoint xử lý yêu cầu đăng nhập hệ thống."""
    service = AuthService(db)
    result = await service.sign_in(payload)
    return ok(
        data=result,
        message="Sign in successful",
        status_code=status.HTTP_200_OK,
    )
