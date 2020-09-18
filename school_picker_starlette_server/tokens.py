from __future__ import annotations

from abc import abstractmethod
from datetime import datetime, timedelta
from enum import IntEnum
from typing import List, Type, TypeVar
from uuid import uuid4

from jose import jwt
from jose.constants import ALGORITHMS
from pydantic import BaseModel
from starlette.datastructures import Secret

from school_picker_starlette_server.validation import User

from .config import config
from .db import database
from .sql import token_blacklist, users

DEFAULT_JWT_ALGORITHM = ALGORITHMS.HS256
SIGNING_KEY = config("TOKEN_SIGNING_KEY", cast=Secret)


T = TypeVar("T", bound="Token")


class InvalidTokenError(Exception):
    def __init__(self) -> None:
        super().__init__("This token is invalid or expired.")


class TokenType(IntEnum):
    access = 1
    refresh = 2


DEFAULT_TOKEN_TYPE = TokenType.access
DEFAULT_LIFETIME = timedelta(minutes=5)


class TokenClaims(BaseModel):
    token_type: str
    exp: float
    sub: str
    iat: float
    jti: str


class BlacklistedToken(BaseModel):
    id: int
    jti: str


class TokenValidator:
    @abstractmethod
    async def validate_token_claims(self, cls: Type[T], claims: TokenClaims) -> bool:
        pass


class TokenLifetimeValidator(TokenValidator):
    async def validate_token_claims(self, cls: Type[T], claims: TokenClaims):
        print(datetime.fromtimestamp(claims.exp))
        print(datetime.utcnow())
        print(datetime.fromtimestamp(claims.exp) >= datetime.utcnow())
        return datetime.fromtimestamp(claims.exp) >= datetime.utcnow()


class TokenJTIValidator(TokenValidator):
    async def validate_token_claims(self, cls: Type[T], claims: TokenClaims) -> bool:
        return bool(claims.jti)


class TokenTypeValidator(TokenValidator):
    async def validate_token_claims(self, cls: Type[T], claims: TokenClaims) -> bool:
        return claims.token_type == cls.token_type.name


class TokenBlacklistValidator(TokenValidator):
    async def validate_token_claims(self, cls: Type[T], claims: TokenClaims) -> bool:
        query = token_blacklist.select(token_blacklist.c.jti == claims.jti)
        row = await database.fetch_one(query)
        return not row


class Token:
    token_type: TokenType
    lifetime: timedelta
    validators: List[TokenValidator]

    def __init__(self, user: User, claims: TokenClaims) -> None:
        self.user = user
        self.claims = claims

    def encode(self) -> str:
        return jwt.encode(
            self.claims.dict(),
            str(SIGNING_KEY),
            algorithm=DEFAULT_JWT_ALGORITHM,
        )

    @classmethod
    async def from_signed_token_string(cls: Type[T], token: str) -> T:
        data = jwt.decode(
            token,
            str(SIGNING_KEY),
            algorithms=DEFAULT_JWT_ALGORITHM,
        )
        claims = TokenClaims(**data)
        for validator in cls.validators:
            if not await validator.validate_token_claims(cls, claims):
                raise InvalidTokenError()
        user = await Token._user_from_sub_claim(claims.sub)
        return cls(user, claims)

    @staticmethod
    async def _user_from_sub_claim(sub_claim: str) -> User:
        user_id = int(sub_claim.split(":")[-1])
        query = users.select(users.c.id == user_id)
        row = await database.fetch_one(query)
        return User(**row)

    @classmethod
    def new_from_user(cls: Type[T], user=User) -> T:
        timestamp = datetime.now()
        claims = TokenClaims(
            token_type=cls.token_type.name,
            exp=datetime.timestamp(timestamp + cls.lifetime),
            sub=f"user:{user.id}",
            iat=datetime.timestamp(timestamp),
            jti=uuid4().hex,
        )
        return cls(user, claims)


class RefreshToken(Token):
    token_type = TokenType.refresh
    lifetime = timedelta(days=1)
    validators = [
        TokenLifetimeValidator(),
        TokenJTIValidator(),
        TokenTypeValidator(),
        TokenBlacklistValidator(),
    ]

    def new_access_token(self) -> AccessToken:
        token = AccessToken.new_from_user(self.user)
        return token

    async def blacklist(self) -> BlacklistedToken:
        query = token_blacklist.insert()
        values = {"jti": self.claims.jti}
        row = await database.execute(query, values)
        return BlacklistedToken(id=row, jti=self.claims.jti)


class AccessToken(Token):
    lifetime = timedelta(minutes=5)
    token_type = TokenType.access
    validators = [
        TokenLifetimeValidator(),
        TokenJTIValidator(),
        TokenTypeValidator(),
    ]
