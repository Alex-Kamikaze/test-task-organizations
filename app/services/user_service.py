from .base_service import BaseService
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user_model import User
from app.exceptions.service_exceptions import UserNotFoundError, IncorrectCredentialsError

class UserService(BaseService):
    """
    Сервис для функционала, связанного с авторизацией и регистрацией пользователей

    """

    async def get_user_token(self, login: str, password: str) -> str:
        """
        Возвращает токен пользователя
        
        Args:
            login (str): Логин пользователя
            password (str): Пароль пользователя

        Returns:
            token (str): Токен пользователя

        Raises:
            UserNotFoundError: Если пользователь с указанным логином/паролем не найден
            IncorrectCredentialsError: Если предоставлены неверные данные для авторизации
        """
        
        stmt = select(User).where(User.login == login)
        query = await self.session.execute(stmt)
        user = query.scalar()
        if not user:
            raise UserNotFoundError()
        
        if user.check_user_password(password, user.password):
            return user.token
        else:
            raise IncorrectCredentialsError()
        
    async def register_user(self, login: str, password: str) -> str:
        """
        Регистрирует нового пользователя в базе и возвращает его токен
        
        Args:
            login (str): Логин пользователя
            password (str): Пароль пользователя

        Raises:
            InvalidCredentialsError: Если логин пользователя не уникальный
        """

        stmt = select(User).where(User.login == login)
        query = await self.session.execute(stmt)
        user_exists = query.scalar()
        if user_exists:
            raise IncorrectCredentialsError()
        
        new_user = User(login=login, password=User.hash_user_password(password))
        await self.session.add(new_user)
        await self.session.commit()
        return new_user.token
        