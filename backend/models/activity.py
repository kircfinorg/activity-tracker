from pydantic import BaseModel, Field
from datetime import datetime

class Activity(BaseModel):
    id: str
    family_id: str
    name: str
    unit: str
    rate: float = Field(gt=0)
    created_by: str
    created_at: datetime
    
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
