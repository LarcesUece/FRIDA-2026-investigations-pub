from typing import Annotated
from fastapi import Depends

from .repositories import DatasetRepositoryDep
from app.services.dataset import DatasetService
from app.services.anonymization import AnonymizationService



def get_dataset_service(dataset_repository: DatasetRepositoryDep) -> DatasetService:
    return DatasetService(dataset_repository)

def get_anonymization_service(
    dataset_repository: DatasetRepositoryDep,
    dataset_service: DatasetService = Depends(get_dataset_service),
) -> AnonymizationService:
    return AnonymizationService(dataset_repository, dataset_service)

DatasetServiceDep = Annotated[DatasetService, Depends(get_dataset_service)]
AnonymizationServiceDep = Annotated[AnonymizationService, Depends(get_anonymization_service)]