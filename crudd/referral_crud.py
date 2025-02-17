from datetime import datetime
import secrets
import string
from typing import Dict, Optional

from fastapi import HTTPException
from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import select

from models import ReferralCode, User


async def get_referrals(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.execute(select(User).filter(User.referrer_id == user_id))
    referrals = result.scalars().all()

    return [{"id": ref.id, "email": ref.email, "referrer_id": ref.referrer_id} for ref in referrals]


async def generate_unique_code(
    db: AsyncSession, length: int = 8, max_attempts: int = 10
) -> Optional[str]:
    alphabet = string.ascii_letters + string.digits

    async def is_code_unique(code: str) -> bool:
        result = await db.execute(
            select(ReferralCode).filter(ReferralCode.code == code)
        )
        return result.scalar() is None

    for _ in range(max_attempts):
        code = "".join(secrets.choice(alphabet) for _ in range(length))
        if await is_code_unique(code):
            return code
    return None


async def create_referral(
    db: AsyncSession, user_id: int
) -> Optional[ReferralCode] | Dict:
    try:
        existing_code = await db.execute(
            select(ReferralCode).filter(ReferralCode.owner_id == user_id)
        )
        existing_code = existing_code.scalars().first()
        if existing_code:
            if existing_code.expires_at > datetime.utcnow():
                return {
                    "message": "У вас уже есть действующий реферальный код. Удалите, если хотите создать новый.",
                    "code": existing_code.code,
                }

        await db.execute(delete(ReferralCode).where(ReferralCode.owner_id == user_id))
        await db.commit()

        code = await generate_unique_code(db)
        if not code:
            raise ValueError("Не удалось сгенерировать уникальный код.")

        referral_code = ReferralCode(
            code=code,
            owner_id=user_id,
        )
        db.add(referral_code)
        await db.commit()
        await db.refresh(referral_code)

        result = await db.execute(
            select(ReferralCode)
            .filter(ReferralCode.owner_id == user_id)
        )
        referral_codes = result.scalars().all()

        return {'message': f'Ваш действующий реферальный код {referral_code.code}'}
    except Exception as e:
        await db.rollback()  # Откат изменений в случае ошибки
        return {"Ошибка при создании реферального кода": str(e)}


async def delete_referrals_by_user_id(db: AsyncSession, user_id: int) -> Dict:
    try:
        result = await db.execute(
            select(ReferralCode).filter(ReferralCode.owner_id == user_id)
        )
        referral_codes = result.scalars().all()

        await db.execute(delete(ReferralCode).where(ReferralCode.owner_id == user_id))
        await db.commit()

        result_after_deletion = await db.execute(
            select(ReferralCode).filter(ReferralCode.owner_id == user_id)
        )
        remaining_codes = result_after_deletion.scalars().all()

        if not remaining_codes:
            return {"message": f"Реферальный код был удален"}
        else:
            return {
                "message": f"Удаление не получилось. Остались коды.",
                "remaining_codes": remaining_codes,
            }

    except Exception as e:
        return {"message": f"Ошибка при удалении реферальных кодов: {str(e)}"}


async def get_referral_code_by_email(db: AsyncSession, email: str):
    query = select(ReferralCode).join(User).where(User.email == email)
    result = await db.execute(query)
    return result.scalars().all()
