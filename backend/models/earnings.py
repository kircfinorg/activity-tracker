from pydantic import BaseModel

class Earnings(BaseModel):
    pending: float
    verified: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "pending": 5.50,
                "verified": 12.75
            }
        }
