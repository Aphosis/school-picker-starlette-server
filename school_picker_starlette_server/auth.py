from typing import Union

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from starlette.authentication import AuthenticationError

from .db import database
from .sql import users
from .validation import User

hasher = PasswordHasher()


async def authenticate(email: str, password: str) -> User:
    error = AuthenticationError("Invalid email or password.")
    user = await _get_user_by_email(email)
    if not user:
        raise error

    if not _verify_password(user.hashed_password, password):
        raise error

    return user


async def _get_user_by_email(email: str) -> Union[User, None]:
    query = users.select(users.c.email == email)
    row = await database.fetch_one(query)
    return User(**row) if row else None


def _verify_password(hashed_password: str, password: str) -> bool:
    try:
        return hasher.verify(hashed_password, password)
    except VerificationError:
        return False
