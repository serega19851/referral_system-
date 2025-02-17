from fastapi import FastAPI

from routers.auth_api import auth_router
from routers.referrals_api import referrals_router


app = FastAPI()

app.include_router(auth_router)
app.include_router(referrals_router)
