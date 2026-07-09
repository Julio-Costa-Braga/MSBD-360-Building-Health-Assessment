from pydantic import BaseModel, Field


class RecommendationCreate(BaseModel):
    code: str = Field(..., max_length=20)
    title: str = Field(..., max_length=255)
    description: str
    category: str = Field(..., max_length=50)
    priority: str = "medium"


class RecommendationRead(BaseModel):
    id: int
    code: str
    title: str
    description: str
    category: str
    priority: str
    is_active: bool

    model_config = {"from_attributes": True}
