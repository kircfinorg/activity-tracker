from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class LogEntry(BaseModel):
    id: str
    activity_id: str
    user_id: str
    family_id: str
    units: int = Field(gt=0)
    timestamp: datetime
    verification_status: Literal["pending", "approved", "rejected"]
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "log123",
                "activity_id": "activity123",
                "user_id": "user456",
                "family_id": "family123",
                "units": 5,
                "timestamp": "2024-01-01T12:00:00Z",
                "verification_status": "pending",
                "verified_by": None,
                "verified_at": None
            }
        }
