from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.database import get_db_session
from src.core.security import (
    verify_password,
    decode_access_token,
    hash_password,
    create_access_token,
)
from src.core.config import settings

from src.domain.models.entities import User
from src.domain.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
)

from src.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    payload: UserRegisterRequest, session: AsyncSession = Depends(get_db_session)
):

    existing_user_stmt = select(User).where(User.email == payload.email)
    existing_user_res = await session.execute(existing_user_stmt)

    if existing_user_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address already exists.",
        )

    new_user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user


@router.post("/login", response_model=TokenResponse)
async def login_user(
    payload: UserLoginRequest, session: AsyncSession = Depends(get_db_session)
):

    existing_user_stmt = select(User).where(User.email == payload.email)
    existing_user_res = await session.execute(existing_user_stmt)
    user = existing_user_res.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=str(user.id))
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user
