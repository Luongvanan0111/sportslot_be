from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class SignInRequest(BaseModel):
    """Schema dữ liệu đầu vào cho yêu cầu đăng nhập."""

    identifier: str = Field(
        ...,
        min_length=1,
        description="Địa chỉ Email hoặc Tên đăng nhập (Username)",
    )
    password: str = Field(
        ...,
        min_length=6,
        description="Mật khẩu tài khoản",
    )


class RefreshTokenRequest(BaseModel):
    """Schema dữ liệu đầu vào cho yêu cầu làm mới access token."""

    refresh_token: str = Field(
        ...,
        min_length=1,
        description="Chuỗi Refresh Token cần làm mới",
    )


class LogoutRequest(BaseModel):
    """Schema dữ liệu đầu vào tùy chọn khi đăng xuất."""

    refresh_token: str | None = Field(
        default=None,
        description="Chuỗi Refresh Token cụ thể cần thu hồi (tùy chọn)",
    )


class UserProfileResponse(BaseModel):
    """Schema thông tin hồ sơ rút gọn trả về kèm User."""

    model_config = ConfigDict(from_attributes=True)

    full_name: str | None = None
    avatar_url: str | None = None
    phone_number: str | None = None
    gender: str | None = None
    date_of_birth: date | None = None
    address: str | None = None


class UserAuthResponse(BaseModel):
    """Schema dữ liệu chi tiết User trả về sau khi xác thực thành công."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    username: str
    status: str
    verified_at: datetime | None = None
    last_login_at: datetime | None = None
    profile: UserProfileResponse | None = None
    roles: list[str] = []
    permissions: list[str] = []


class SignInResponseData(BaseModel):
    """Cấu trúc dữ liệu trường data trong phản hồi đăng nhập và làm mới token."""

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    user: UserAuthResponse
