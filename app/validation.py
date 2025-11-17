from pydantic import BaseModel, Field

class Property(BaseModel):
    title: str
    description: str
    price: float = Field(gt=0)
    location: str
    rooms: int = Field(gt=0)
