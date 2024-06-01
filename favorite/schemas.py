from pydantic import BaseModel


class UserFavoriteTarotsCreate(BaseModel):
    user_id: int
    tarot_id: int


class UserFavoriteTarotsOut(BaseModel):
    favorite_tarot_id: int
    user_id: int
    tarot_id: int
