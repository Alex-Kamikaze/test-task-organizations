from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.db_dependency import provide_session
from app.services.user_service import UserService
from app.api.models.login import TokenResponse, LoginRequest
from app.exceptions.service_exceptions import (
    UserNotFoundError,
    IncorrectCredentialsError,
)

auth_router = APIRouter()


@auth_router.post(
    "/token",
    response_model=TokenResponse,
    summary="Получение токена по логину и паролю",
)
async def issue_token(
    payload: LoginRequest,
    session: Annotated[AsyncSession, Depends(provide_session)],
) -> TokenResponse:
    service = UserService(session)
    try:
        token = await service.get_user_token(payload.login, payload.password)
        return TokenResponse(token=token)
    except UserNotFoundError:
        raise HTTPException(
            status_code=401, detail="Не найдено пользователя с указанным логином"
        )
    except IncorrectCredentialsError:
        raise HTTPException(status_code=401, detail="Неверные логин/пароль")


@auth_router.post(
    "/register",
    summary="Регистрация пользователя",
    description="Региструет нового пользователя в базе и возвращает его токен",
    response_model=TokenResponse,
    responses={
        400: {
            "description": "Пользователь с таким логином уже существует",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Пользователь с указанным логином уже существует"
                    }
                }
            },
        }
    },
)
async def register_user(
    session: Annotated[AsyncSession, Depends(provide_session)],
    login: str = Query(description="Логин пользователя"),
    password: str = Query(description="Пароль пользователя"),
) -> TokenResponse:
    service = UserService(session)
    try:
        token = await service.register_user(login, password)
        return TokenResponse(token=token)
    except IncorrectCredentialsError:
        raise HTTPException(detail="Пользователь с таким логином уже существует")
