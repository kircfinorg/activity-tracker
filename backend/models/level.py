from pydantic import BaseModel

class UserLevel(BaseModel):
    user_id: str
    level: int
    experience_points: int
    total_experience: int
    
    @property
    def experience_to_next_level(self) -> int:
        """Calculate XP needed for next level (exponential growth)"""
        return 100 * (self.level ** 1.5)
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress to next level as percentage"""
        xp_needed = self.experience_to_next_level
        return (self.experience_points / xp_needed) * 100 if xp_needed > 0 else 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "level": 5,
                "experience_points": 250,
                "total_experience": 1250
            }
        }
