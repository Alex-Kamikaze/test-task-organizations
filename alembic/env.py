import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from dotenv import load_dotenv

from app.db.models.base_model import Model
from app.db.models.organisation_models import (
    Organisation,
    OrganisationPhones,
    OrganisationActivities,
)
from app.db.models.activity_models import Activity
from app.db.models.building_models import Building
from app.db.models.user_model import User

load_dotenv()


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Model.metadata


def get_database_url():
    """Получение URL базы данных из переменных окружения"""
    return os.getenv("ALEMBIC_DB_URI")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""

    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    # Получаем URL базы данных
    database_url = get_database_url()

    # Обновляем конфигурацию с правильным URL
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = database_url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
