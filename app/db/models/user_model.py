from os import urandom
from sqlalchemy import Column, String, Integer
import bcrypt
from .base_model import Model

def generate_token() -> str:
    """
    Генерирует рандомный токен для пользователя

    Returns:
        token (str): Сгенерированный токен
    """

    initial = urandom(20)
    result = bcrypt.hashpw(initial, bcrypt.gensalt())
    return result.decode()


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
    password = Column(String, nullable=False)
    token = Column(String, unique=True, nullable=False, default=generate_token)

    def __str__(self):
        return self.login

    @staticmethod
    def hash_user_password(password: str) -> str:
        """
        Хэширует пароль для дальнейшего сохранения в базу

        Args:
            password (str): Исходный пароль

        Returns:
            hashed_password (str): Хэшированный пароль
        """
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        return hashed_password.decode()

    @staticmethod
    def check_user_password(password: str, hashed_password: str) -> bool:
        """
        Проверяет пароль пользователя на соответствие хэшу

        Args:
            password (str): Введенный пароль
            hashed_password (str): Хэш пароля

        Returns:
            result (bool): Результат проверки
        """
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
