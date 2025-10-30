from typing import List
from pydantic import BaseModel
from .activity import ActivityModel

class Organization(BaseModel):
    """
    Модель организации в слое бизнес-логики

    Attributes:
        id (int):  ID организации
        name (str): Название организции
        address (str): Адрес организации
        phones (List[str]): Телефоны организации
        activities (List[Activity]): Виды деятельности организации
    """
    id: int
    name: str
    address: str
    phones: List[str]
    activities: List[ActivityModel]