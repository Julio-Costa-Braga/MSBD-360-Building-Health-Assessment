from datetime import datetime

from pydantic import BaseModel, Field


class MeasurementCreate(BaseModel):
    sub_location: str | None = None
    temperature: float | None = Field(None, ge=-10, le=60)
    relative_humidity: float | None = Field(None, ge=0, le=100)
    co2: float | None = Field(None, ge=0, le=10000)
    surface_temperature: float | None = Field(None, ge=-10, le=60)
    material_moisture: float | None = Field(None, ge=0, le=100)
    illuminance: float | None = Field(None, ge=0, le=200000)
    observations: str | None = None


class MeasurementUpdate(BaseModel):
    sub_location: str | None = None
    temperature: float | None = Field(None, ge=-10, le=60)
    relative_humidity: float | None = Field(None, ge=0, le=100)
    co2: float | None = Field(None, ge=0, le=10000)
    surface_temperature: float | None = Field(None, ge=-10, le=60)
    material_moisture: float | None = Field(None, ge=0, le=100)
    illuminance: float | None = Field(None, ge=0, le=200000)
    observations: str | None = None


class MeasurementRead(BaseModel):
    id: int
    room_id: int
    sub_location: str | None
    temperature: float | None
    relative_humidity: float | None
    co2: float | None
    surface_temperature: float | None
    material_moisture: float | None
    illuminance: float | None
    observations: str | None
    measured_at: datetime

    model_config = {"from_attributes": True}
