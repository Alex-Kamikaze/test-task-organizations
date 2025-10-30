from typing import Annotated
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies.db_dependency import provide_session
from app.services.organization_services import OrganizationService, LocationService
from app.exceptions.service_exceptions import (
    OrganizationNotFoundError,
    NoOrganizationsFoundError,
    NoBuildingsFoundError,
    ActivityNotFoundError
)

organizations_router = APIRouter()


@organizations_router.get(
    "/get_organization_by_activity_id",
    summary="Список организаций по виду деятельности",
    description="Возвращает список организаций, занимающихся указанным видом деятельности",
    responses={
        404: {
            "description": "Не найдено организаций с указанным видом деятельности",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Не найдено организаций, занимающихся указанным видом деятельности"
                    }
                }
            },
        },
    },
)
async def get_organization_by_activity_id(
    session: Annotated[AsyncSession, Depends(provide_session)],
    activity_id: int = Query(description="ID вида деятельности"),
):
    service = OrganizationService(session)
    try:
        result = await service.get_organizations_by_activity_id(activity_id)
        return result
    except NoOrganizationsFoundError:
        raise HTTPException(
            status_code=404,
            detail="Не найдено организаций, занимающихся указанным видом деятельности",
        )


@organizations_router.get(
    "/search_organization_by_name",
    summary="Поиск организаций по имени",
    description="Ищет список организаций по имени",
    responses={
        404: {
            "description": "Не найдено организаций, подходящих под условия",
            "content": {
                "application/json": {
                    "example": {"detail": "Не найдено подходящих организаций"}
                }
            },
        },
    },
)
async def search_organizations(
    session: Annotated[AsyncSession, Depends(provide_session)],
    name: str = Query(description="Название организации"),
):
    service = OrganizationService(session)
    try:
        result = await service.search_organization_by_name(name)
        return result
    except NoOrganizationsFoundError:
        raise HTTPException(status_code=404, detail="Не найдено подходящих организаций")


@organizations_router.get(
    "/get_organization_by_id",
    summary="Получение организации по идентификатору",
    description="Возвращает информацию об организации по ее идентификатору",
    responses={
        404: {
            "description": "Не найдено организаций, подходящих под условия",
            "content": {
                "application/json": {"example": {"detail": "Организация не найдена"}}
            },
        },
    },
)
async def get_organization_by_id(
    session: Annotated[AsyncSession, Depends(provide_session)],
    organization_id: int = Query(description="Идентификатор организации"),
):
    service = OrganizationService(session)
    try:
        result = await service.get_organization_by_id(organization_id)
        return result
    except OrganizationNotFoundError:
        raise HTTPException(status_code=404, detail="Организация не найдена")


@organizations_router.get(
    "/get_organizations_within_radius",
    summary="Поиск организаций в радиусе",
    description="Ищет организации в зданиях, расположенные в указанном радиусе",
    responses={
        404: {
            "description": "Не найдено зданий/организаций в указанном радиусе",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Не найдено зданий в указанном радиусе / Не найдено организаций в указанном радиусе"
                    }
                }
            },
        }
    },
)
async def get_organizations_within_radius(
    session: Annotated[AsyncSession, Depends(provide_session)],
    center_lan: float = Query(description="Широта центральной точки"),
    center_lon: float = Query(description="Долгота центральной точки"),
    radius_km: float = Query(description="Радиус в километрах"),
):
    service = LocationService(session)
    try:
        result = await service.get_organizations_in_radius(
            center_lan, center_lon, radius_km
        )
        return result
    except NoBuildingsFoundError:
        raise HTTPException(
            status_code=404, detail="Не найдено зданий в указанном радиусе"
        )
    except NoOrganizationsFoundError:
        raise HTTPException(
            status_code=404, detail="Не найдено организаций в указанном радиусе"
        )


@organizations_router.get(
    "/get_organizations_within_square",
    summary="Получение организаций в прямоугольной области",
    description="Возвращает список организаций в прямоугольной области по координатам",
    responses={
        404: {
            "description": "Не найдено зданий/организаций в указанной области",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Не найдено зданий в указанной области / Не найдено организаций в указанной области"
                    }
                }
            },
        }
    },
)
async def get_organizations_within_square(
    session: Annotated[AsyncSession, Depends(provide_session)],
    ne_lat: float = Query(description="Северо-восточная широта"),
    ne_lon: float = Query(description="Северо-восточная долгота"),
    sw_lat: float = Query(description="Юго-западная широта"),
    sw_lon: float = Query(description="Юго-западная долгота"),
):
    service = LocationService(session)
    try:
        results = await service.get_organizations_in_square(
            ne_lat, ne_lon, sw_lat, sw_lon
        )
        return results
    except NoBuildingsFoundError:
        raise HTTPException(
            status_code=404, detail="Не найдено зданий в указанной области"
        )
    except NoOrganizationsFoundError:
        raise HTTPException(
            status_code=404, detail="Не найдено организаций в указанной области"
        )


@organizations_router.get(
    "/search_organization_with_activities",
    summary="Поиск организаций по дереву видов деятельности",
    description="Ищет организации, составляя дерево видов деятельности, и возвращая все организации, которые занимаются найденными видами деятельности",
    responses={
        404: {
            "description": "Не найдено вида деятельности / организаций, подходящих под условия",
            "content": {
                "application/json": {"example": {"detail": "Не найдено указанного вида деятельности / Не найдено организаций, подходящих под условия"}}
            }
        }
    }
)
async def search_organization_with_activities(session: Annotated[AsyncSession, Depends(provide_session)], activity_id: int = Query(description="ID вида деятельности")):
    service = OrganizationService(session)
    try:
        result = service.search_organizations_with_activities(activity_id)
        return result
    except NoOrganizationsFoundError:
        raise HTTPException(status_code=404, detail="Не найдено организаций, подходящих под условия")
    except ActivityNotFoundError:
        raise HTTPException(status_code=404, detail="Не найдено указанного вида деятельности")