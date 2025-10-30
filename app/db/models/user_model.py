from os import urandom
from sqlalchemy import Column, String, Integer
from aiobcrypt import checkpw, hashpw, gensalt
from bcrypt import hashpw as sync_hashpw, gensalt as sync_gensalt
from .base_model import Model

def generate_token() -> str:
    """
    Генерирует рандомный токен для пользователя

    Returns:
        token (str): Сгененрированный токен
    """

    intiial = str(urandom(20)).replace("b'", "").replace("'", "").replace("\x00", "")
    result = sync_hashpw(bytes(intiial, encoding="utf-8"), sync_gensalt())
    return str(result).replace("b'", "").replace("'", "")



class User(Model):
    """
    Модель пользователя с токеном для авторизации

    Attributes:
        id (int): ID пользователя
        login (str): Логин для авторизации
        password (str): Хэшированный пароль
        token (str): Токен для авторизации
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, unique=True, nullable=False)
    token = Column(String, unique=True, nullable=False, default=generate_token)

    def __str__(self):
        return self.login
    
    @staticmethod
    async def hash_user_password(password: str) -> str:
        """
        Хэширует пароль для дальнейшего сохранения в базу

        Args:
            password (str): Исходный пароль

        Returns:
            hashed_password (str): Хэшированный пароль
        """
        hashed_password = await hashpw(bytes(password, encoding="utf-8"), await gensalt())
        
        return str(hashed_password).replace("b'", "").replace("'", "")
    
    @staticmethod
    async def check_user_password(password: str, hashed_password: str) -> bool:
        """
        Проверяет пароль пользователя на соответствие хэшу
        
        Args:
            password (str): Введенный пароль
            hashed_password (str): Хэш пароля

        Returns:
            result (bool): Результат проверки
        """

        return await checkpw(bytes(password, encoding="utf-8"), bytes(hashed_password, encoding="utf-8"))