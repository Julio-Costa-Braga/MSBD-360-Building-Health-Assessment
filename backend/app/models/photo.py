from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    room_id: Mapped[int] = mapped_column(Integer, ForeignKey("rooms.id"), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    caption: Mapped[str] = mapped_column(Text, nullable=True)
    photo_type: Mapped[str] = mapped_column(String(20), nullable=True, default="after")
    photo_data: Mapped[str] = mapped_column(Text, nullable=True)
    taken_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    room: Mapped["Room"] = relationship("Room", back_populates="photos")
