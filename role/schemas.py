from pydantic import BaseModel


class RoleCreate(BaseModel):
    role_name: str


class RoleOut(BaseModel):
    role_id: int
    role_name: str