from pydantic import BaseModel, Field


class MenuItemCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    price: float = Field(gt=0)             # gt = greater than 0
    is_veg: bool = True


class MenuItem(MenuItemCreate):
    id: int                                # response mein id bhi hogi


class MenuItemUpdate(BaseModel):           # PATCH ke liye: sab optional
    name: str | None = Field(default=None, min_length=2, max_length=50)
    price: float | None = Field(default=None, gt=0)
    is_veg: bool | None = None