from typing import List, Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Query, HTTPException
from ..models.organisation import Organization
from ..dependencies.db_dependency import provide_session
from app.services.organization_services import OrganizationService
from app.exceptions.service_exceptions import (
    BuildingNotFoundException,
    BuildingWithNoOrganizationsError,
)

building_router = APIRouter()


@building_router.get(
    "/get_organizations_from_building",
    summary="Список организаций из здания",
    description="Возвращает список организаций, которые находятся в указанном здании",
    responses={
        404: {
            "description": "Не найдено здания, либо в указанном здании нет организаций",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Здание не найдено / В здании не найдено организаций"
                    }
                }
            },
        },
    }
)
async def get_organizations_from_building(
    session: Annotated[AsyncSession, Depends(provide_session)],
    building_id: int = Query(description="ID здания"),
) -> List[Organization]:
    service = OrganizationService(session)
    try:
        organizations = await service.get_organizations_from_specific_building(
            building_id
        )
        return organizations
    except BuildingNotFoundException:
        raise HTTPException(status_code=404, detail="Здание не найдено")
    except BuildingWithNoOrganizationsError:
        raise HTTPException(status_code=404, detail="В здании не найдено организаций")
