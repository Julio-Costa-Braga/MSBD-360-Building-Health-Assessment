from pydantic import BaseModel, Field

from app.utils.enums import RoomType


class RoomCreate(BaseModel):
    name: str = Field(..., max_length=255)
    room_type: RoomType
    floor_level: int = 0
    area_sqm: float | None = None


class RoomUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    room_type: RoomType | None = None
    floor_level: int | None = None
    area_sqm: float | None = None


class RoomRead(BaseModel):
    id: int
    inspection_id: int
    name: str
    room_type: str
    floor_level: int
    area_sqm: float | None

    model_config = {"from_attributes": True}
