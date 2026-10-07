from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError
from app.core.security import decode_token
from app.db.database import get_db_session
from app.db.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)
DBSession = Annotated[AsyncSession, Depends(get_db_session)]


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: DBSession,
) -> User:
    if credentials is None:
        raise AuthenticationError("Authentication credentials were not provided.")

    try:
        payload = decode_token(credentials.credentials)
        user_id = UUID(payload["sub"])
    except Exception as exc:  # noqa: BLE001
        raise AuthenticationError("Invalid or expired authentication token.") from exc

    result = await session.execute(select(User).where(User.id == user_id, User.is_active.is_(True)))
    user = result.scalar_one_or_none()
    if user is None:
        raise AuthenticationError("User account is not available.")
    return user

