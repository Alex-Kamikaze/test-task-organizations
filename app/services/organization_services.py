from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload, aliased
from geopy.distance import geodesic
from app.api.models.organisation import Organization
from .base_service import BaseService
from app.db.models.organisation_models import (
    Organisation,
    OrganisationActivities,
    OrganisationPhones,
)
from app.db.models.activity_models import Activity
from app.db.models.building_models import Building
from app.mappers.organization_mapper import OrganizationMapper
from app.exceptions.service_exceptions import (
    BuildingWithNoOrganizationsError,
    BuildingNotFoundException,
    NoOrganizationsFoundError,
    OrganizationNotFoundError,
    NoBuildingsFoundError,
    ActivityNotFoundError,
)


class OrganizationService(BaseService):
    async def get_organizations_from_specific_building(
        self, building_id: int
    ) -> List[Organization]:
        """
        Возвращает список организаций, расположенных в определенном здании

        Args:
            building_id (int): ID здания

        Returns:
            organizations (List[Organization]): Список организаций, находящихся в этом здании

        Raises:
            BuildingNotFoundException: Если указанного здания не найдено
            BuildingWithNoOrganizationsError: Если в указанном здании нет организаций
        """
        stmt = (
            select(Building)
            .where(Building.id == building_id)
            .options(
                selectinload(Building.organisations).options(
                    selectinload(Organisation.phones),
                    selectinload(Organisation.organisation_activities).selectinload(
                        OrganisationActivities.activity
                    ),
                )
            )
        )

        building = await self.session.scalar(stmt)

        if not building:
            raise BuildingNotFoundException(f"Building with id {building_id} not found")

        if not building.organisations:
            raise BuildingWithNoOrganizationsError(
                f"Building {building_id} has no organizations"
            )

        return [
            OrganizationMapper.convert(instance) for instance in building.organisations
        ]

    async def get_organizations_by_activity_id(
        self, activity_id: int
    ) -> List[Organization]:
        """
        Возвращает список организаций, занимающихся указанным видом деятельности

        Args:
            activity_id (int): ID Вида деятельности

        Returns:
            organizations (List[Organization]): Список организаций, занимающихся указанным видом деятельности

        Raises:
            NoOrganizationsFoundError: Если не найдено организаций, занимающихся указанным видом деятельности
        """

        stmt = (
            select(Organisation)
            .join(Organisation.organisation_activities)
            .where(OrganisationActivities.activity_id == activity_id)
            .options(
                selectinload(Organisation.phones),
                selectinload(Organisation.organisation_activities).selectinload(
                    OrganisationActivities.activity
                ),
                selectinload(Organisation.building),
            )
            .distinct()
        )

        result = await self.session.execute(stmt)
        organizations = result.scalars().all()
        if not organizations:
            raise NoOrganizationsFoundError()

        return [OrganizationMapper.convert(instance) for instance in organizations]

    async def search_organization_by_name(self, name: str) -> List[Organization]:
        """
        Ищет организации по совпадению по имени

        Args:
            name (str): Название, по котором необходимо искать

        Returns:
            organizations (List[Organization]): Список организаций

        Raises:
            NoOrganizationsFoundError: Если не найдено организаций, подходящих под условия
        """
        stmt = (
            select(Organisation)
            .where(Organisation.name.ilike(f"%{name}%"))
            .options(
                selectinload(Organisation.phones),
                selectinload(Organisation.organisation_activities).selectinload(
                    OrganisationActivities.activity
                ),
                selectinload(Organisation.building),
            )
        )

        result = await self.session.execute(stmt)
        organizations = result.scalars().all()
        if not organizations:
            raise NoOrganizationsFoundError()

        return [OrganizationMapper.convert(instance) for instance in organizations]

    async def get_organization_by_id(self, organization_id: int) -> Organization:
        """
        Возвращает информацию об организации по ее ID

        Args:
            organization_id (int): ID организации

        Returns:
            out (Organization): Информация об организации

        Raises:
            OrganizationNotFoundError: Если организация не найдена
        """
        stmt = (
            select(Organisation)
            .where(Organisation.id == organization_id)
            .options(
                selectinload(Organisation.phones),
                selectinload(Organisation.organisation_activities).selectinload(
                    OrganisationActivities.activity
                ),
                selectinload(Organisation.building),
            )
        )
        result = await self.session.execute(stmt)
        organization = result.scalar()
        if not organization:
            raise OrganizationNotFoundError()

        return OrganizationMapper.convert(organization)

    async def search_organizations_with_activities(
        self, activity_id: int
    ) -> List[Organization]:
        """
        Возвращает список организаций, которые занимаются указанными видами деятельности (включая дочерние виды деятельности)

        Args:
            activity_id (int): Вид деятельности

        Returns:
            organizations (List[Organization]): Список организаций

        Raises:
            ActivityNotFoundError: Не найдено указанного вида деятельности
            NoOrganizationsFoundError: Не найдено организаций, которые имеют указанные виды деятельности
        """

        check_query = await self.session.execute(
            select(Activity.id).where(Activity.id == activity_id)
        )
        if not check_query.scalar():
            raise ActivityNotFoundError()

        activity_tree = (
            select(Activity.id)
            .where(Activity.id == activity_id)
            .cte(name="activity_tree", recursive=True)
        )
        a_child = aliased(Activity)
        activity_tree = activity_tree.union_all(
            select(a_child.id).where(a_child.parent == activity_tree.c.id)
        )

        stmt = (
            select(Organisation)
            .join(Organisation.organisation_activities)
            .where(OrganisationActivities.activity_id.in_(select(activity_tree.c.id)))
            .options(
                selectinload(Organisation.phones),
                selectinload(Organisation.organisation_activities).selectinload(
                    OrganisationActivities.activity
                ),
                selectinload(Organisation.building),
            )
            .distinct()
        )

        query = await self.session.execute(stmt)
        organizations = query.scalars().all()

        if not organizations:
            raise NoOrganizationsFoundError()

        return [OrganizationMapper.convert(organization) for organization in organizations]


class LocationService(BaseService):
    """
    Сервис с функциями для поиска зданий по координатам
    """

    async def __get_buildings_within_range(
        self, center_latitude: float, center_longitude: float, radius_km: float
    ) -> Optional[List[Building]]:
        """
        Возвращает список зданий в указанном радиусе

        Args:
            center_latitude (float): Географическая ширина указанной точки
            center_longitude (float): Географическая долгота указанной точки
            radius_km (float): Радиус поиска в километрах

        Returns:
            buildings (Optional[List[Building]]): Список зданий в указанном радиусе
        """
        center_point = (center_latitude, center_longitude)
        stmt = select(Building).where(
            Building.latitude.isnot(None), Building.longitude.isnot(None)
        )
        query = await self.session.execute(stmt)
        buildings = query.scalars().all()
        result = []

        if not buildings:
            return None

        for building in buildings:
            building_point = (building.latitude, building.longitude)
            distance = geodesic(center_point, building_point).kilometers

            if distance <= radius_km:
                result.append(building)

        return result

    async def __get_building_in_square(
        self, ne_lat: float, ne_lon: float, sw_lat: float, sw_lon: float
    ) -> Optional[List[Building]]:
        """
        Возвращает список зданий в указанной прямоугольной области на карте

        Args:
            ne_lat (float): Серверо-восточная широта
            ne_lon (float): Серверо-восточная долгота
            sw_lat (float): Юго-западная широта
            sw_lon (float): Юго-западная долгота

        Returns:
            buildings (Optional[List[Building]]): Список зданий в указанной области
        """

        stmt = select(Building).where(
            Building.latitude.isnot(None),
            Building.longitude.isnot(None),
            Building.latitude.between(sw_lat, ne_lat),
            Building.longitude.between(sw_lon, ne_lon),
        )

        query = await self.session.execute(stmt)
        result = query.scalars().all()
        return result

    async def get_organizations_in_radius(
        self, center_latitude: float, center_longitude: float, radius_km: float
    ) -> List[Organization]:
        """
        Возвращает список организаций в указанном радиусе

        Args:
            center_latitude (float): Географическая ширина указанной точки
            center_longitude (float): Географическая долгота указанной точки
            radius_km (float): Радиус поиска в километрах

        Returns:
            organizations (List[Organization]): Список организаций в указанном радиусе

        Raises:
            NoBuildingsFoundError: Если в указанном радиусе не найдено зданий
            NoOrganizationsFoundError: Если в указанном радиусе не найдено организаций
        """

        buildings = await self.__get_buildings_within_range(
            center_latitude, center_longitude, radius_km
        )
        result: List[Organization] = []
        if not buildings:
            raise NoBuildingsFoundError()

        buildings_ids = [building.id for building in buildings]
        organization_service = OrganizationService(self.session)
        for building_id in buildings_ids:
            try:
                organizations = await organization_service.get_organizations_from_specific_building(
                    building_id
                )
                result.extend(organizations)
            except BuildingWithNoOrganizationsError:
                continue

        if not result:
            raise NoOrganizationsFoundError()

        return result

    async def get_organizations_in_square(
        self, ne_lat: float, ne_lon: float, sw_lat: float, sw_lon: float
    ) -> List[Organization]:
        """
        Возвращает список организаций в указанной прямоугольной области на карте

        Args:
            ne_lat (float): Серверо-восточная широта
            ne_lon (float): Серверо-восточная долгота
            sw_lat (float): Юго-западная широта
            sw_lon (float): Юго-западная долгота

        Returns:
            organization (List[Organization]): Список организаций в указанной области

        Raises:
            NoBuildingsFoundError: Если в указанной области не найдено зданий
            NoOrganizationsFoundError: Если в указанной области не найдено организаций
        """

        buildings = await self.__get_building_in_square(ne_lat, ne_lon, sw_lat, sw_lon)
        result: List[Organization] = []
        if not buildings:
            raise NoBuildingsFoundError()

        organization_service = OrganizationService(self.session)

        buildings_ids = [building.id for building in buildings]
        for building_id in buildings_ids:
            try:
                organizations = await organization_service.get_organizations_from_specific_building(
                    building_id
                )
                result.extend(organizations)
            except BuildingWithNoOrganizationsError:
                continue

        if not result:
            raise NoOrganizationsFoundError()

        return result
