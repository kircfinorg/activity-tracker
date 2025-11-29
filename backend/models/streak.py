from pydantic import BaseModel
from datetime import datetime

class UserStreak(BaseModel):
    user_id: str
    current_streak: int
    longest_streak: int
    last_activity_date: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "current_streak": 7,
                "longest_streak": 15,
                "last_activity_date": "2024-01-01T00:00:00Z"
            }
        }
