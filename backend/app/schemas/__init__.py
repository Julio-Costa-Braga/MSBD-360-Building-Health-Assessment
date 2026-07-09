from app.schemas.inspection import InspectionCreate, InspectionRead, InspectionUpdate
from app.schemas.room import RoomCreate, RoomRead, RoomUpdate
from app.schemas.measurement import MeasurementCreate, MeasurementRead, MeasurementUpdate
from app.schemas.photo import PhotoCreate, PhotoRead
from app.schemas.recommendation import RecommendationCreate, RecommendationRead

__all__ = [
    "InspectionCreate", "InspectionRead", "InspectionUpdate",
    "RoomCreate", "RoomRead", "RoomUpdate",
    "MeasurementCreate", "MeasurementRead", "MeasurementUpdate",
    "PhotoCreate", "PhotoRead",
    "RecommendationCreate", "RecommendationRead",
]
