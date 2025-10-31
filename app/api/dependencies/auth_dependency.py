from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .db_dependency import provide_session
from app.db.models.user_model import User

_bearer_scheme = HTTPBearer(auto_error=False)

async def require_bearer_auth(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(_bearer_scheme)],
    session: Annotated[AsyncSession, Depends(provide_session)],
) -> str:
    """
    Проверяет Bearer-токен в заголовке Authorization. В случае несоответствия кидает 401

    Returns:
        token (str): Токен авторизованного пользователя

    Raises:
        HTTPException: Если не предоставлена информация для авторизации или пользователь не найден
    """
    if credentials is None or (credentials.scheme or "").lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = credentials.credentials
    query = await session.execute(select(User).where(User.token == token))
    user = query.scalar()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    return user