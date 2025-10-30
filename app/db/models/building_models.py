from sqlalchemy import Column, String, Integer, Float
from sqlalchemy.orm import relationship
from .base_model import Model

class Building(Model):
    """
    Здание, в котором может располагаться организация

    Attributes:
        id (int): ID здания
        address (str): Уникальный адрес здания
        latitude (str): Географическая широта, на котрой расположено здание
        longitude (str): Географическая долгота, на которой расположено здание
    """
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    address = Column(String, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)

    organisations = relationship("Organisation", backref="building", lazy="selectin")

    def __str__(self):
        return self.address