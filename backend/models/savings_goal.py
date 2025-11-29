from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class SavingsGoal(BaseModel):
    id: str
    user_id: str
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    target_amount: float = Field(gt=0)
    current_amount: float = Field(ge=0, default=0)
    created_at: datetime
    completed_at: Optional[datetime] = None
    is_completed: bool = False
    icon: str = "🎯"  # Emoji icon
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress as percentage"""
        return (self.current_amount / self.target_amount) * 100 if self.target_amount > 0 else 0
    
    @property
    def remaining_amount(self) -> float:
        """Calculate remaining amount to reach goal"""
        return max(0, self.target_amount - self.current_amount)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "goal123",
                "user_id": "user123",
                "name": "New Bike",
                "description": "Save for a mountain bike",
                "target_amount": 200.00,
                "current_amount": 75.50,
                "created_at": "2024-01-01T00:00:00Z",
                "completed_at": None,
                "is_completed": False,
                "icon": "🚴"
            }
        }
