from sqlalchemy.ext.asyncio import AsyncSession

class BaseService:
    """
    Базовый класс для всех классов с бизнес-логикой
    """
    def __init__(self, db_session: AsyncSession):
        self.session = db_session