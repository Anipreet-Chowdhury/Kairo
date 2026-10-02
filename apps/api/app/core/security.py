from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from jwt.exceptions import InvalidTokenError

from app.core.config import get_settings
from app.schemas.auth import AuthenticatedUser

bearer_scheme = HTTPBearer()

settings = get_settings()

jwks_url = f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"

jwks_client = PyJWKClient(jwks_url)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
) -> AuthenticatedUser:
    token = credentials.credentials

    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated",
            issuer=f"{settings.supabase_url.rstrip('/')}/auth/v1",
        )

        user_id = UUID(payload["sub"])
        return AuthenticatedUser(user_id=user_id)

    except (InvalidTokenError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        ) from None
