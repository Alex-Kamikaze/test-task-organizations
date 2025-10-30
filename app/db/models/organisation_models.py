from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from .base_model import Model
from .building_models import Building
from .activity_models import Activity


class Organisation(Model):
    """
    Модель организаций в базе

    Attributes:
        id (int): ID организации
        name (str): Название организации
        building (Building): Здание, в котором расположена организация
        phones (List[str]): Список телефонных номеров организации
        activities (List[Activity]): Список видов деятельности организации

    """

    __tablename__ = "organisations"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, nullable=False, unique=True)
    building_id = Column(Integer, ForeignKey("buildings.id"))

    phones = relationship(
        "OrganisationPhones",
        backref="organisation_phones",
        foreign_keys="OrganisationPhones.organisation_id",
        lazy="selectin",
    )

    organisation_activities = relationship(
        "OrganisationActivities",
        back_populates="organisation",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    activities = association_proxy("organisation_activities", "activity")

    def __str__(self):
        return self.name


class OrganisationPhones(Model):
    """
    Список номеров телефонов для организаций

    Attributes:
        phone_id (int): Уникальный ID телефона
        organisation_id (int): Внешний ключ к организации, которой принадлежит номер телефона
        phone (String): Номер телефона
    """

    __tablename__ = "organisation_phones"

    phone_id = Column(Integer, primary_key=True, autoincrement=True)
    organisation_id = Column(Integer, ForeignKey("organisations.id"))
    phone = Column(String, unique=True)

    organisation = relationship("Organisation", back_populates="phones")

    def __str__(self):
        return self.phone


class OrganisationActivities(Model):
    """
    Список видов деятельности, которыми может заниматься организация

    Attributes:
        link_id (int): Уникальный номер записи
        organisation_id (ForeignKey(int)): Ссылка на организацию
        activity_id (ForeignKey(int)): Ссылка на вид/подвид деятельности
    """

    __tablename__ = "organisation_actvities"

    link_id = Column(Integer, primary_key=True, autoincrement=True)
    organisation_id = Column(
        Integer, ForeignKey("organisations.id", ondelete="cascade"), index=True
    )
    activity_id = Column(Integer, ForeignKey("activities.id"), index=True)

    organisation = relationship(
        "Organisation", back_populates="organisation_activities"
    )

    activity = relationship(
        "Activity", back_populates="organisation_activities", lazy="selectin"
    )

    def __str__(self):
        return f"{self.organisation_id}: {self.activity_id}"
