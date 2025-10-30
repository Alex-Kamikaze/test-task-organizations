from typing import List
from app.api.models.organisation import Organization
from app.db.models.organisation_models import Organisation, OrganisationActivities, OrganisationPhones
from app.db.models.activity_models import Activity
from app.api.models.activity import ActivityModel

class OrganizationMapper:
    """
    Маппер для преобразования модели организации уровня базы данных в уровень бизнес-логики
    """

    @staticmethod
    def convert(db_model: Organisation) -> Organization:
        phones = OrganizationPhonesMapper.convert(db_model.phones)
        activities = OrganizationActivitiesMapper.convert(db_model.activities)
        return Organization(id = db_model.id, name=db_model.name, address=db_model.building.address, phones=phones, activities=activities)

class OrganizationPhonesMapper:
    """
    Маппер для преобразования модели телефонов организации в список из строк
    """

    @staticmethod
    def convert(db_models: List[OrganisationPhones]) -> List[str]:
        """
        Преобразует сущность телефона организации в строку

        Args:
            db_models (List[OrganisationPhones]): Список сущностей

        Returns:
            phones (str): Список строк с номерами телефонов
        """
        return [instance.phone for instance in db_models]
    
class OrganizationActivitiesMapper:
    """
    Маппер для преобразования модели вида деятельности из базы в модель слоя бизнес-логики
    """

    @staticmethod
    def convert(activities: List[Activity]) -> List[ActivityModel]:
        """
        Конвертирует модель вида деятельности уровня базы в уровень бизнес-логики
        Args:
            activities (List[Activity]): Виды деятельности из базы

        Returns:
            mapped_activities (List[ActivityModel]): Модели вида деятельности уровня бизнес логики
        """
        return [ActivityModel(id=activity.id, name=activity.name) for activity in activities]