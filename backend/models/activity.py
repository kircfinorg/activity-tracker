from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class Activity(BaseModel):
    id: str
    family_id: str
    name: str = Field(min_length=1, description="Activity name must not be empty")
    unit: str = Field(min_length=1, description="Unit must not be empty")
    rate: float = Field(gt=0, description="Rate must be a positive value")
    created_by: str
    created_at: datetime
    
    @field_validator('name', 'unit')
    @classmethod
    def validate_not_empty_or_whitespace(cls, v: str, info) -> str:
        """Validate that name and unit are not empty or only whitespace"""
        if not v or not v.strip():
            raise ValueError(f'{info.field_name} must not be empty or only whitespace')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "activity123",
                "family_id": "family123",
                "name": "Reading",
                "unit": "Pages",
                "rate": 0.10,
                "created_by": "user123",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
