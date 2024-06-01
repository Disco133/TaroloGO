from pydantic import BaseModel


class UserFavoriteTarotsCreate(BaseModel):
    user_id: int
    tarot_id: int


class UserFavoriteTarotsOut(BaseModel):
    tarot_id: int
