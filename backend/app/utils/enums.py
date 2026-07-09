from enum import StrEnum


class RoomType(StrEnum):
    BEDROOM = "bedroom"
    LIVING_ROOM = "living_room"
    KITCHEN = "kitchen"
    BATHROOM = "bathroom"
    OFFICE = "office"
    HALLWAY = "hallway"
    BASEMENT = "basement"
    ATTIC = "attic"
    OTHER = "other"


class InspectionStatus(StrEnum):
    DRAFT = "draft"
    COMPLETED = "completed"


class ISACategory(StrEnum):
    EXCELLENT = "excellent"
    ACCEPTABLE = "acceptable"
    NEEDS_INTERVENTION = "needs_intervention"
    HIGH_RISK = "high_risk"


class Pillar(StrEnum):
    THERMAL = "thermal"
    HUMIDITY = "humidity"
    VENTILATION = "ventilation"
    MATERIALS = "materials"
    LIGHTING = "lighting"
    VISUAL = "visual"


class RecommendationPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
