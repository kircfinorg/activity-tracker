from pydantic import BaseModel
from typing import List
from datetime import datetime

class Family(BaseModel):
    id: str
    invite_code: str
    owner_id: str
    members: List[str]
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "family123",
                "invite_code": "ABC123",
                "owner_id": "user123",
                "members": ["user123", "user456"],
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
