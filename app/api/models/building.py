from pydantic import BaseModel

class BuildingModel(BaseModel):
    """
    Модель здания в слое бизнес-логики

    Attributes:
        id (int): ID здания
        address (str): Адрес здания
        latitude (float): Географическая широта здания
        longitude (float): Географическая долгота здания
    """

    id: int
    address: str
    latitude: float
    longitude: float