from datetime import timedelta

from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from auth import create_access_token, verify_password
from crudd.user_crud import create_user, get_user_by_email, UserCreate
from database import get_async_session
from settings import ACCESS_TOKEN_EXPIRE_MINUTES


auth_router = APIRouter()


@auth_router.post(
    "/auth/register/",
    tags=["Auth"],
    description="Регистрация нового пользователя. Принимает email и пароль, создает нового пользователя в базе данных. Поле referral опционально",
)
async def register_user(
    user: UserCreate, db: AsyncSession = Depends(get_async_session)
):
    db_user = await get_user_by_email(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await create_user(db, user)


@auth_router.post("/login/", tags=["Auth"])
async def login_user(
    db: AsyncSession = Depends(get_async_session),
    username: str = Form(...),
    password: str = Form(...),
) -> dict:
    db_user = await get_user_by_email(db, username)
    if not db_user or not await verify_password(password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(
        data={"id": db_user.id, "email": db_user.email},
        expires_delta=timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)),
    )
    return {"access_token": access_token, "token_type": "bearer"}
