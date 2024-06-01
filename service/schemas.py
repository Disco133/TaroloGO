from pydantic import BaseModel, Field


class ServiceCreate(BaseModel):
    service_name: str
    tarot_id: int = Field(..., ge=1)
    specialization_id: int = Field(..., ge=1)
    service_price: int

class ServiceOut(BaseModel):
    service_id: int
    service_name: str
    service_price: int