from pydantic import BaseModel, Field
from pydantic import BaseModel, ConfigDict, Field
from app.order_status import OrderStatus


class MenuItemCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    price: float = Field(gt=0)             # gt = greater than 0
    is_veg: bool = True
    stock: int = Field(default=100, ge=0)

class MenuItem(MenuItemCreate):
    model_config = ConfigDict(from_attributes=True)   # ORM object ko response mein badalne ke liye
    id: int

class MenuItemUpdate(BaseModel):           # PATCH ke liye: sab optional
    name: str | None = Field(default=None, min_length=2, max_length=50)
    price: float | None = Field(default=None, gt=0)
    is_veg: bool | None = None
    stock: int | None = Field(default=None, ge=0)

class UserCreate(BaseModel):
    email: str = Field(min_length=5, max_length=100)
    password: str = Field(min_length=8, max_length=72)


class UserPublic(BaseModel):          # response mein password/hash kabhi nahi
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"    


class OrderItemIn(BaseModel):
    menu_item_id: int
    quantity: int = Field(gt=0, le=20)


class OrderCreate(BaseModel):
    items: list[OrderItemIn] = Field(min_length=1)


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    menu_item_id: int
    quantity: int
    price_at_order: float


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: str
    total: float
    items: list[OrderItemOut]    

class OrderStatusUpdate(BaseModel):
    status: OrderStatus    

class RestaurantCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    cuisine: str = Field(min_length=2, max_length=50)
    rating: float = Field(default=0.0, ge=0, le=5)
    is_veg: bool = False


class RestaurantOut(RestaurantCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class RestaurantPage(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[RestaurantOut]    