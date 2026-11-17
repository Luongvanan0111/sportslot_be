from enum import StrEnum


class UserStatus(StrEnum):
    UNVERIFIED = "unverified"
    ACTIVATED = "activated"
    BANNED = "banned"


class RoleEnum(StrEnum):
    ADMIN = "admin"
    OWNER = "owner"
    USER = "user"


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


class Gender(StrEnum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
