from pydantic import BaseModel


class StatusCreate(BaseModel):
   status_name: str


class StatusOut(BaseModel):
   status_id: int
   status_name: str