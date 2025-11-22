from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class User(BaseModel):
    uid: str
    email: str
    display_name: str
    photo_url: str
    role: Literal["parent", "child"]
    family_id: Optional[str] = None
    theme: str = "deep-ocean"
    created_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "uid": "abc123",
                "email": "user@example.com",
                "display_name": "John Doe",
                "photo_url": "https://example.com/photo.jpg",
                "role": "parent",
                "family_id": "family123",
                "theme": "deep-ocean"
            }
        }
