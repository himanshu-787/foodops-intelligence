from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.schemas import RestaurantCreate, RestaurantOut, RestaurantPage

router = APIRouter(prefix="/restaurants", tags=["restaurants"])


@router.post("", response_model=RestaurantOut, status_code=201)
def create_restaurant(data: RestaurantCreate, db: Session = Depends(get_db)):
    obj = models.Restaurant(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("", response_model=RestaurantPage)
def search_restaurants(
    q: str | None = Query(default=None, min_length=2, description="Naam mein search"),
    cuisine: str | None = None,
    min_rating: float = Query(default=0, ge=0, le=5),
    is_veg: bool | None = None,
    sort: str = Query(default="rating", pattern="^(rating|name)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),   # max limit: koi 1 lakh nahi maang sakta
    db: Session = Depends(get_db),
):
    stmt = select(models.Restaurant).where(models.Restaurant.rating >= min_rating)

    if q:
        stmt = stmt.where(models.Restaurant.name.ilike(f"%{q}%"))
    if cuisine:
        stmt = stmt.where(func.lower(models.Restaurant.cuisine) == cuisine.lower())
    if is_veg is not None:
        stmt = stmt.where(models.Restaurant.is_veg == is_veg)

    # Total count (pagination UI ke liye), filters ke baad
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))

    if sort == "rating":
        stmt = stmt.order_by(models.Restaurant.rating.desc(), models.Restaurant.id)
    else:
        stmt = stmt.order_by(models.Restaurant.name, models.Restaurant.id)

    stmt = stmt.limit(page_size).offset((page - 1) * page_size)
    items = db.scalars(stmt).all()

    return {"total": total, "page": page, "page_size": page_size, "items": items}