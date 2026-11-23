"""Hằng số thông điệp chuẩn hóa toàn hệ thống (100% English Constants)."""


class CommonMsg:
    SUCCESS = "Success"
    NOT_FOUND = "Resource not found"
    UNAUTHORIZED = "Unauthorized access"
    FORBIDDEN = "Forbidden access"
    BAD_REQUEST = "Bad request"
    INTERNAL_SERVER_ERROR = "Internal server error"


class AuthMsg:
    SIGN_IN_SUCCESS = "Sign in successful"
    SIGN_OUT_SUCCESS = "Sign out successful"
    INVALID_CREDENTIALS = "Email/username or password incorrect"
    ACCOUNT_BANNED = "Account has been banned"
    ACCOUNT_LOCKED = "Account is temporarily locked"
    TOKEN_EXPIRED = "Token has expired"
    TOKEN_INVALID = "Invalid token"
    REFRESH_TOKEN_SUCCESS = "Token refreshed successfully"
    USER_NOT_FOUND = "User does not exist"
    NOT_AUTHENTICATED = "Not authenticated"


class RoleMsg:
    ROLE_NOT_FOUND = "Role not found"
    ROLE_NAME_EXISTS = "Role name already exists"
    SYSTEM_ROLE_PROTECTED = "System core role cannot be modified or deleted"
    CANNOT_DELETE_ROLE_WITH_USERS = "Cannot delete role assigned to active users"


class TermMsg:
    TERM_NOT_FOUND = "Term version not found"
    TERM_VERSION_EXISTS = "Term version already exists"
    ACTIVE_TERM_PROTECTED = "Active term cannot be deleted"
    CANNOT_ACTIVATE_EXPIRED_TERM = "Cannot activate expired term version"
