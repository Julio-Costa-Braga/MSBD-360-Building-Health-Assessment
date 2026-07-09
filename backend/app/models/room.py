from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    inspection_id: Mapped[int] = mapped_column(Integer, ForeignKey("inspections.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    room_type: Mapped[str] = mapped_column(String(50), nullable=False)
    floor_level: Mapped[int] = mapped_column(Integer, default=0)
    area_sqm: Mapped[float] = mapped_column(Float, nullable=True)

    inspection: Mapped["Inspection"] = relationship("Inspection", back_populates="rooms")
    measurements: Mapped[list["Measurement"]] = relationship("Measurement", back_populates="room", cascade="all, delete-orphan")
    photos: Mapped[list["Photo"]] = relationship("Photo", back_populates="room", cascade="all, delete-orphan")
    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation", secondary="room_recommendations", back_populates="rooms"
    )
