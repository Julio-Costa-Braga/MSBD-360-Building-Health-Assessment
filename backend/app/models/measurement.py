from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Measurement(Base):
    __tablename__ = "measurements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    room_id: Mapped[int] = mapped_column(Integer, ForeignKey("rooms.id"), nullable=False)
    temperature: Mapped[float] = mapped_column(Float, nullable=True)
    relative_humidity: Mapped[float] = mapped_column(Float, nullable=True)
    co2: Mapped[float] = mapped_column(Float, nullable=True)
    surface_temperature: Mapped[float] = mapped_column(Float, nullable=True)
    material_moisture: Mapped[float] = mapped_column(Float, nullable=True)
    illuminance: Mapped[float] = mapped_column(Float, nullable=True)
    observations: Mapped[str] = mapped_column(Text, nullable=True)
    measured_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    room: Mapped["Room"] = relationship("Room", back_populates="measurements")
