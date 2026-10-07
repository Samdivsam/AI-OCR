from fastapi import APIRouter, Depends, status
from sqlalchemy import select

from app.api.deps import DBSession, get_current_user
from app.core.exceptions import AuthenticationError, BadRequestError
from app.core.security import create_access_token, hash_password, verify_password
from app.db.models.user import User
from app.schemas.auth import TokenResponse, UserLoginRequest, UserRegisterRequest, UserResponse
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegisterRequest, session: DBSession) -> TokenResponse:
    existing = await session.execute(select(User).where(User.email == payload.email.lower()))
    if existing.scalar_one_or_none() is not None:
        raise BadRequestError("EMAIL_ALREADY_EXISTS", "An account with this email already exists.")

    user = User(email=payload.email.lower(), password_hash=hash_password(payload.password))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return TokenResponse(access_token=create_access_token(user.id), user=UserResponse.model_validate(user))


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLoginRequest, session: DBSession) -> TokenResponse:
    result = await session.execute(select(User).where(User.email == payload.email.lower()))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise AuthenticationError("Invalid email or password.")
    return TokenResponse(access_token=create_access_token(user.id), user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.post("/logout", response_model=MessageResponse)
async def logout(_: User = Depends(get_current_user)) -> MessageResponse:
    return MessageResponse(message="Logged out successfully.")

