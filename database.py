from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from settings import ASYNC_SQLALCHEMY_DATABASE_URL

engine = create_async_engine(
    ASYNC_SQLALCHEMY_DATABASE_URL, connect_args={}, pool_size=6
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


Base = declarative_base()
