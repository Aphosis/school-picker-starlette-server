from typing import Optional

from password_strength import PasswordStats
from pydantic import BaseModel, EmailStr, validator

SECURE_PASSWORD_STRENGTH = 0.66


def validate_password_strength(password):
    if password is not None:
        stats = PasswordStats(password)
        if stats.strength() < SECURE_PASSWORD_STRENGTH:
            raise ValueError(
                "Your password is insecure. "
                "Try adding more symbols or numbers, mixing upper and lower case, "
                "and having a longer password."
            )
    return password


def validate_confirm_password(confirm_password, values):
    if "password" in values:
        assert confirm_password == values["password"], ValueError(
            "Passwords do not match"
        )
    return confirm_password


class User(BaseModel):
    id: int
    email: EmailStr
    hashed_password: str


class CreateUserInput(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str

    _validate_password_strength = validator("password", allow_reuse=True)(
        validate_password_strength
    )
    _validate_confirm_password = validator("confirm_password", allow_reuse=True)(
        validate_confirm_password
    )


class UpdateUserInput(BaseModel):
    id: int
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    confirm_password: Optional[str] = None

    _validate_password_strength = validator("password", allow_reuse=True)(
        validate_password_strength
    )
    _validate_confirm_password = validator("confirm_password", allow_reuse=True)(
        validate_confirm_password
    )


class ObtainTokenPairInput(BaseModel):
    email: EmailStr
    password: str


class TokenPairResponse(BaseModel):
    access: str
    refresh: str


class AccessTokenResponse(BaseModel):
    access: str
