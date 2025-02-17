from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import verify_token
from crudd.referral_crud import (
    create_referral,
    delete_referrals_by_user_id,
    get_referral_code_by_email,
    get_referrals,
)
from database import get_async_session
from models import User

referrals_router = APIRouter()


@referrals_router.post("/referrals/code/", tags=["Referrals"], description="Создает новый реферальный код если его нет или если он уже устарел по времени")
async def create_referral_code(
    payload: dict = Depends(verify_token), db: AsyncSession = Depends(get_async_session)
):
    referral_codes = await create_referral(db, payload["id"])
    return f"{referral_codes} "


@referrals_router.delete("/referrals/code/", tags=["Referrals"], description="Удаляет реферальный код пользователя" )
async def delete_referral_code(
    payload: dict = Depends(verify_token), db: AsyncSession = Depends(get_async_session)
):
    dell_ref = await delete_referrals_by_user_id(db, payload["id"])
    return f"{dell_ref} "


@referrals_router.get("/referrals/code/", tags=["Referrals"], description="Получает свой реферальный код по своему емаил")
async def get_referral(
    email: str,
    payload: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_async_session),
):
    # Проверяем, что email из запроса совпадает с email в токене
    if email != payload.get("email"):
        raise HTTPException(
            status_code=403, detail="Нет доступа к данным другого пользователя"
        )

    # Если email совпадает, продолжаем выполнение
    referral_code = await get_referral_code_by_email(db, email)
    if referral_code:
        return {"referral_code": referral_code}
    else:
        raise HTTPException(status_code=404, detail="Реферальный код не найден")


# @referrals_router.get("/referrals/code/", tags=["Referrals"])
# async def get_referral(
#     email: str,
#     payload: dict = Depends(verify_token),
#     db: AsyncSession = Depends(get_async_session),
# ):
#     referral_code = await get_referral_code_by_email(db, email)
#     if referral_code:
#         return {"referral_code": referral_code}
#     else:
#         raise HTTPException(status_code=404, detail="Реферальный код не найден")


@referrals_router.get("/users/{user_id}/referrals", tags=["Referrals"])
async def get_user_referrals(
    user_id: int = Path(..., description="ID рефера, чьи рефералы запрашиваются"),
    payload: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_async_session),
):
    current_user_id = payload.get("id")

    if user_id != current_user_id:
        raise HTTPException(
            status_code=403, detail="Нет доступа к рефералам другого пользователя"
        )

    referrals = await get_referrals(db, user_id)
    return referrals


# @referrals_router.get("/users/{user_id}/referrals", tags=["Referrals"])
# async def get_user_referrals(
#     user_id: int, db: AsyncSession = Depends(get_async_session)
# ):
#     referrals = await get_referrals(db, user_id)
#     return referrals


######################################################
async def delete_all_users(db: AsyncSession):
    async with db.begin():
        result = await db.execute(select(User))
        users = result.scalars().all()

        for user in users:
            await db.delete(user)

    await db.commit()


@referrals_router.delete("/users/delete/")
async def delete_referral_code(db: AsyncSession = Depends(get_async_session)):
    await delete_all_users(db)
    return {"message": "All users have been deleted"}
