from pydantic import BaseModel, Field
from pydantic import BaseModel, ConfigDict, Field


class MenuItemCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    price: float = Field(gt=0)             # gt = greater than 0
    is_veg: bool = True


class MenuItem(MenuItemCreate):
    model_config = ConfigDict(from_attributes=True)   # ORM object ko response mein badalne ke liye
    id: int

class MenuItemUpdate(BaseModel):           # PATCH ke liye: sab optional
    name: str | None = Field(default=None, min_length=2, max_length=50)
    price: float | None = Field(default=None, gt=0)
    is_veg: bool | None = None


class UserCreate(BaseModel):
    email: str = Field(min_length=5, max_length=100)
    password: str = Field(min_length=8, max_length=72)


class UserPublic(BaseModel):          # response mein password/hash kabhi nahi
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"    