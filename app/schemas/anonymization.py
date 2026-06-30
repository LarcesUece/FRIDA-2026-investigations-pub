from pydantic import BaseModel, Field
from typing import List, Any

class MaskingConfig(BaseModel):
    column_name: str
    method: str
    params: dict[str, Any] = Field(default_factory=dict)

class ProportionalColumn(BaseModel):
    column_name: str
    alpha: float = Field(gt=0, lt=1)


class ProportionalRequest(BaseModel):
    columns: List[ProportionalColumn]


class StructureAwareColumn(BaseModel):
    column_name: str
    p: int = Field(ge=0)
    q: int = Field(ge=0)


class StructureAwareRequest(BaseModel):
    columns: List[StructureAwareColumn]