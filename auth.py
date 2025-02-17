from datetime import datetime, timedelta, timezone
from typing import Optional
from asyncio import to_thread
from fastapi import Depends, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from settings import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def verify_password(plain_password, hashed_password):
    return await to_thread(pwd_context.verify, plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = (
        datetime.now(timezone.utc) + expires_delta
        if expires_delta
        else timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


