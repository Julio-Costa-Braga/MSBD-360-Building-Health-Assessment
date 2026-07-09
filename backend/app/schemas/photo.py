from datetime import datetime

from pydantic import BaseModel


class PhotoCreate(BaseModel):
    caption: str | None = None


class PhotoRead(BaseModel):
    id: int
    room_id: int
    file_path: str
    caption: str | None
    taken_at: datetime

    model_config = {"from_attributes": True}
