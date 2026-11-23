from fastapi import APIRouter, status

from app.core.deps import CurrentUser, DbSession
from app.core.messages import AuthMsg, CommonMsg
from app.schemas.auth import (
    LogoutRequest,
    RefreshTokenRequest,
    SignInRequest,
    SignInResponseData,
    UserAuthResponse,
)
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
        message=AuthMsg.SIGN_IN_SUCCESS,
        status_code=status.HTTP_200_OK,
    )


@router.post(
    "/refresh-token",
    response_model=ApiResponse[SignInResponseData],
    status_code=status.HTTP_200_OK,
    summary="Làm mới Access Token bằng Refresh Token",
    description="Thu hồi refresh token cũ, cấp mới cặp access token và refresh token.",
)
async def refresh_token(
    payload: RefreshTokenRequest,
    db: DbSession,
) -> ApiResponse[SignInResponseData]:
    """Endpoint làm mới token phiên làm việc."""
    service = AuthService(db)
    result = await service.refresh_token(payload.refresh_token)
    return ok(
        data=result,
        message=AuthMsg.REFRESH_TOKEN_SUCCESS,
        status_code=status.HTTP_200_OK,
    )


@router.post(
    "/logout",
    response_model=ApiResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Đăng xuất và thu hồi phiên làm việc",
    description="Thu hồi refresh token trong cơ sở dữ liệu và dọn sạch phiên người dùng.",
)
async def logout(
    current_user: CurrentUser,
    db: DbSession,
    payload: LogoutRequest | None = None,
) -> ApiResponse[None]:
    """Endpoint xử lý yêu cầu đăng xuất."""
    service = AuthService(db)
    token_str = payload.refresh_token if payload else None
    await service.logout(current_user.id, token_str)
    return ok(
        data=None,
        message=AuthMsg.SIGN_OUT_SUCCESS,
        status_code=status.HTTP_200_OK,
    )


@router.get(
    "/me",
    response_model=ApiResponse[UserAuthResponse],
    status_code=status.HTTP_200_OK,
    summary="Lấy thông tin tài khoản hiện tại",
    description="Giải mã Bearer token và trả về thông tin profile, roles và permissions của người dùng đang đăng nhập.",
)
async def get_me(
    current_user: CurrentUser,
    db: DbSession,
) -> ApiResponse[UserAuthResponse]:
    """Endpoint đồng bộ profile và phân quyền của tài khoản hiện tại."""
    service = AuthService(db)
    result = await service.get_me(current_user)
    return ok(
        data=result,
        message=CommonMsg.SUCCESS,
        status_code=status.HTTP_200_OK,
    )
