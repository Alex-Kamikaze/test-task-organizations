from pydantic import BaseModel

class LoginRequest(BaseModel):
    """
    Данные из запроса для авторизации пользователя
    
    Attributes:
        login (str): Логин пользователя
        password (str): Пароль пользователя
    """
    login: str
    password: str

class TokenResponse(BaseModel):
    """
    Ответ с токеном пользователя
    
    Attributes:
        token (str): Токен пользователя
    """
    token: str