from pydantic import BaseModel


class SpecCreate(BaseModel):
    specialization_name: str


class SpecOut(BaseModel):
    specialization_id: int
    specialization_name: str


class TarotSpecializationCreate(BaseModel):
    specialization_id: int
    tarot_id: int


class TarotSpecializationOut(BaseModel):
    tarot_specialization_id: int
    specialization_id: int
    tarot_id: int
