from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Badge(BaseModel):
    id: str
    name: str
    description: str
    icon: str  # Emoji or icon identifier
    category: str  # 'activity', 'earnings', 'streak', 'special'
    requirement_type: str  # 'count', 'total', 'streak', 'special'
    requirement_value: int
    rarity: str  # 'common', 'rare', 'epic', 'legendary'
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "badge_first_activity",
                "name": "First Steps",
                "description": "Log your first activity",
                "icon": "🎯",
                "category": "activity",
                "requirement_type": "count",
                "requirement_value": 1,
                "rarity": "common"
            }
        }


class UserBadge(BaseModel):
    user_id: str
    badge_id: str
    earned_at: datetime
    progress: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "badge_id": "badge_first_activity",
                "earned_at": "2024-01-01T00:00:00Z",
                "progress": 100
            }
        }
