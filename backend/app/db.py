from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.ext.asyncio.session import create_async_engine
from sqlmodel.ext.asyncio.session import sessionmaker

from app.config import settings

# SQLite async URL example: sqlite+aiosqlite:///./data.db
engine = create_async_engine(
    settings.database_url.replace("sqlite://", "sqlite+aiosqlite://"),
    echo=False,
    future=True,
)
SessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    session: AsyncSession = SessionLocal()
    try:
        yield session
    finally:
        await session.close()


