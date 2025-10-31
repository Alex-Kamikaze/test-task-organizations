## Настройки проекта
В корневой директории необходимо создать .env файл со следующими параметрами:
```
ALEMBIC_DB_URI="..." URL для подключения к базе при использовании миграций
SQLALCHEMY_DB_URI="..." URL для подключения к базе в приложении
HOST="0.0.0.0"
PORT=8000
DEBUG=FALSE
POSTGRES_USER="user"
POSTGRES_PASSWORD="password"
POSTGRES_DB="organisations_db"
```

## Запуск проекта
При первом запуске:
```
docker compose up --build -d
docker compose exec web uv run alembic upgrade head
```

В дальнейшем:
```
docker compose up -d
```

## Документация
Swagger - /docs
ReDoc - /redoc