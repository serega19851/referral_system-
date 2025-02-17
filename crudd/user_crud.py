from datetime import datetime
from typing import Optional
from fastapi import HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import select

from auth import get_password_hash
from models import ReferralCode, User

class UserCreate(BaseModel):
    username: EmailStr
    password: str
    referral: Optional[str] = None

async def create_user(db: AsyncSession, user: UserCreate):
    referrer = None
    if user.referral:
        result = await db.execute(
            select(ReferralCode).filter(ReferralCode.code == user.referral)
        )
        referral_code = result.scalars().first()
        if not referral_code or referral_code.expires_at < datetime.utcnow():
            raise HTTPException(status_code=400, detail="Invalid referral code")

        result = await db.execute(
            select(User).filter(User.id == referral_code.owner_id)
        )
        referrer = result.scalars().first()

    hashed_password = get_password_hash(user.password)

    db_user = User(
        email=user.username,
        hashed_password=hashed_password,
        referrer_id=referrer.id if referrer else None,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(
        select(User)
        .options(selectinload(User.referral_code))
        .filter(User.email == email)
    )
    return result.scalars().first()
