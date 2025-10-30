from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class ApplicationSettings(BaseSettings):
    """

    Настройки приложения из файла окружения

    Attributes:
        ALEMBIC_DB_URI (str): URI-строка для подключения к базе в Alembic
        SQLALCHEMY_DB_URI (str): URI-строка для подключения к базе в API (нужно потому, что используется асинхронный драйвер PostgreSQL, который не поддерживается в Alembic. Для него используется синхронный Psycopg2)
        DEBUG (bool): Флаг включения режима отладки
        HOST (str): Хост, на котром будет запускаться приложение
        PORT (int): Порт, на котором будет работать приложение

    """

    ALEMBIC_DB_URI: str = Field(alias="ALEMBIC_DB_URI")
    SQLALCHEMY_DB_URI: str = Field(alias="SQLALCHEMY_DB_URI")
    DEBUG: bool = Field(alias="DEBUG")
    HOST: str = Field(alias="HOST")
    PORT: int = Field(alias="PORT")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

app_settings = ApplicationSettings()