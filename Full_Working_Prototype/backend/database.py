import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://aura_user:aura_pass_hackathon@localhost/aura_db"
)

#engine = create_async_engine(DATABASE_URL, echo=True)
engine = create_async_engine(DATABASE_URL, echo=os.environ.get("SQL_ECHO", "true").lower() == "true")
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session() as session:
        yield session
