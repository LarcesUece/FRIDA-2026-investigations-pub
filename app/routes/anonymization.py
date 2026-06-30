from fastapi import APIRouter

from app.api.v1.dependencies.auth import CurrentUser
from app.api.v1.dependencies.services import AnonymizationServiceDep

from app.schemas.anonymization import (
    ProportionalRequest,
    StructureAwareRequest
)

router = APIRouter() 

#in progress
@router.post("/{dataset_id}/anonymize/proportional")
async def anonymize_proportional(
    dataset_id: int,
    request: ProportionalRequest,
    current_user: CurrentUser,
    service: AnonymizationServiceDep
):
    return await service.anonymize_proportional(
        dataset_id,
        request,
        current_user
    )

#in progress
@router.post("/{dataset_id}/anonymize/structure-aware")
async def anonymize_structure(
    dataset_id: int,
    request: StructureAwareRequest,
    current_user: CurrentUser,
    service: AnonymizationServiceDep
):
    return await service.anonymize_structure_aware(
        dataset_id,
        request,
        current_user
    )