import logging

from app.orders import router as orders_router

from app.restaurants import router as restaurants_router

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.database import Base, engine, get_db

from app.errors import register_error_handlers
from app.errors import EmptyCartError
from app.middleware import log_requests
from fastapi import FastAPI, HTTPException
from fastapi import FastAPI, HTTPException, status
from app.schemas import MenuItem, MenuItemCreate, MenuItemUpdate
from app.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FoodOps API")
Base.metadata.create_all(bind=engine)   # tables bana deta hai (Phase 8+ mein Alembic migrations)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app.middleware("http")(log_requests)
register_error_handlers(app)
app.include_router(auth_router)
app.include_router(orders_router)
app.include_router(restaurants_router)

# Abhi ke liye fake data (database Phase 5 mein aayega)
restaurants = [
    {"id": 1, "name": "Biryani House", "cuisine": "Mughlai", "rating": 4.5},
    {"id": 2, "name": "Dosa Corner", "cuisine": "South Indian", "rating": 4.2},
    {"id": 3, "name": "Pizza Point", "cuisine": "Italian", "rating": 4.0},
]

@app.get("/")
def health_check():
    return {"status": "ok", "service": "FoodOps"}


@app.get("/restaurants")
def list_restaurants(cuisine: str | None = None):
    if cuisine:
        return [r for r in restaurants if r["cuisine"].lower() == cuisine.lower()]
    return restaurants


@app.get("/restaurants/{restaurant_id}")
def get_restaurant(restaurant_id: int):
    for r in restaurants:
        if r["id"] == restaurant_id:
            return r
    raise HTTPException(status_code=404, detail="Restaurant not found")


# Fake in-memory storage (Phase 5 mein database aayega)
menu_items: list[dict] = []
next_id = 1


@app.post("/menu", response_model=MenuItem, status_code=status.HTTP_201_CREATED, tags=["menu"])
def create_menu_item(item: MenuItemCreate, db: Session = Depends(get_db)):
    obj = models.MenuItem(**item.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)          # DB ne jo id banayi woh wapas lao
    return obj


@app.get("/menu", response_model=list[MenuItem], tags=["menu"])
def list_menu_items(db: Session = Depends(get_db)):
    return db.scalars(select(models.MenuItem)).all()


@app.get("/menu/{item_id}", response_model=MenuItem, tags=["menu"])
def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.MenuItem, item_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return obj


@app.patch("/menu/{item_id}", response_model=MenuItem, tags=["menu"])
def update_menu_item(item_id: int, changes: MenuItemUpdate, db: Session = Depends(get_db)):
    obj = db.get(models.MenuItem, item_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    for field, value in changes.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


@app.delete("/menu/{item_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["menu"])
def delete_menu_item(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.MenuItem, item_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    db.delete(obj)
    db.commit()

@app.post("/orders/test")
def test_order(cart: list[float]):
    if not cart:
        raise EmptyCartError("Cart khaali hai")
    return {"total": sum(cart)}


@app.get("/crash")
def crash():
    return 1 / 0        # jaanbujhkar bug, sirf demo ke liye