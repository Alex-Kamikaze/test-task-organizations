from pydantic import BaseModel

class ActivityModel(BaseModel):
    """
    Модель вида деятельности в слое бизнес-логики

    Attributes:
        id (int): ID вида деятельности
        name (str): Название вида деятельности
    """

    id: int
    name: str