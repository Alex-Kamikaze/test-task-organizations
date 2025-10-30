from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from .base_model import Model

class Activity(Model):
    """
    Вид деятельности, которым может заниматься организация

    Attributes:
        id (int): ID вида деятельности
        name (str): Название вида деятельности
        parent (ForeignKey(int)): Ссылка на основной вид деятельности для подвида. Все виды деятельности, у которых нет parent, являются основными видами, а те, у которых есть - подвидами

    Examples:
        Пример вида деятельности с подвидами:
            Activity(id=1, name="Еда", parent=None) -> Activity(id=2, name="Молочная продукция", parent=1)
    """
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, unique=True)
    parent = Column(Integer, ForeignKey("activities.id", ondelete="cascade"))

    sub_activities = relationship(
        "Activity",
        remote_side=[id],
        backref="subactivities",
        foreign_keys=[parent]
    )
    
    
    organisation_activities = relationship(
        "OrganisationActivities", 
        back_populates="activity"
    )