from datetime import date, datetime

from pydantic import BaseModel, Field


class InspectionCreate(BaseModel):
    client_name: str = Field(..., max_length=255)
    property_address: str
    inspector_name: str = Field(..., max_length=255)
    inspection_date: date
    notes: str | None = None


class InspectionUpdate(BaseModel):
    client_name: str | None = Field(None, max_length=255)
    property_address: str | None = None
    inspector_name: str | None = Field(None, max_length=255)
    inspection_date: date | None = None
    status: str | None = None
    notes: str | None = None


class InspectionRead(BaseModel):
    id: int
    client_name: str
    property_address: str
    inspector_name: str
    inspection_date: date
    status: str
    overall_isa_score: float | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InspectionListItem(BaseModel):
    id: int
    client_name: str
    property_address: str
    inspector_name: str
    inspection_date: date
    status: str
    overall_isa_score: float | None

    model_config = {"from_attributes": True}
