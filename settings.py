from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
ASYNC_SQLALCHEMY_DATABASE_URL = os.getenv('ASYNC_SQLALCHEMY_DATABASE_URL')
EXPIRES_AT= os.getenv("EXPIRES_AT")
