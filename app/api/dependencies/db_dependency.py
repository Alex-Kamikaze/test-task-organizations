from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from ...core.settings import app_settings

async def provide_session():
    """
    Возвращает асинхронную сессию для работы

    Yields:
        async_session (AsyncSession): Асинхронная сессия для работы с базой данных
    
    """
    async_engine = create_async_engine(app_settings.SQLALCHEMY_DB_URI)
    async_session = async_sessionmaker(bind=async_engine)()
    try:
        yield async_session
    finally:
        await async_session.close()