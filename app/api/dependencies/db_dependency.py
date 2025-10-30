from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from ...core.settings import app_settings

_engine = create_async_engine(app_settings.SQLALCHEMY_DB_URI, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(bind=_engine, expire_on_commit=False)

async def provide_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Возвращает асинхронную сессию для работы

    Yields:
        async_session (AsyncSession): Асинхронная сессия для работы с базой данных
    """
    async with AsyncSessionLocal() as session:
        yield session
