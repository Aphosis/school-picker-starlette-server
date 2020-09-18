from .mutation import mutation
from ....auth import authenticate
from ....tokens import BlacklistedToken, RefreshToken
from ....validation import (
    AccessTokenResponse,
    ObtainTokenPairInput,
    TokenPairResponse,
)


@mutation.field("obtainTokenPair")
async def resolve_obtain_token_pair(*_, input) -> TokenPairResponse:
    data = ObtainTokenPairInput(**input)

    user = await authenticate(data.email, data.password)

    refresh_token = RefreshToken.new_from_user(user)
    access_token = refresh_token.new_access_token()

    return TokenPairResponse(
        refresh=refresh_token.encode(),
        access=access_token.encode(),
    )


@mutation.field("refreshToken")
async def resolve_refresh_token(*_, refreshToken: str) -> AccessTokenResponse:
    refresh_token = await RefreshToken.from_signed_token_string(refreshToken)
    access_token = refresh_token.new_access_token()
    response = AccessTokenResponse(access=access_token.encode())
    return response


@mutation.field("blacklistToken")
async def resolve_blacklist_token(*_, refreshToken: str) -> BlacklistedToken:
    refresh_token = await RefreshToken.from_signed_token_string(refreshToken)
    return await refresh_token.blacklist()
