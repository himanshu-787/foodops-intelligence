from fastapi import APIRouter, Depends, Header, HTTPException, Response
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models
from app.auth import get_current_user
from app.database import get_db
from app.schemas import OrderCreate, OrderOut

router = APIRouter(prefix="/orders", tags=["orders"])


def _find_existing(db: Session, user_id: int, key: str):
    return db.scalar(
        select(models.Order).where(
            models.Order.user_id == user_id,
            models.Order.idempotency_key == key,
        )
    )


@router.post("", response_model=OrderOut, status_code=201)
def place_order(
    payload: OrderCreate,
    response: Response,
    idempotency_key: str = Header(min_length=8, max_length=64),
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.scalar(select(models.User).where(models.User.email == email))

    # 1. Same key pehle aa chuki hai? Naya order mat banao, purana wapas do.
    existing = _find_existing(db, user.id, idempotency_key)
    if existing:
        response.status_code = 200
        return existing

    try:
        order = models.Order(user_id=user.id, idempotency_key=idempotency_key, total=0.0)
        total = 0.0

        for line in payload.items:
            item = db.get(models.MenuItem, line.menu_item_id)
            if item is None:
                raise HTTPException(404, f"Menu item {line.menu_item_id} not found")

            # 2. Atomic stock update: check aur update ek hi SQL mein
            result = db.execute(
                update(models.MenuItem)
                .where(
                    models.MenuItem.id == item.id,
                    models.MenuItem.stock >= line.quantity,
                )
                .values(stock=models.MenuItem.stock - line.quantity)
            )
            if result.rowcount == 0:
                raise HTTPException(409, f"'{item.name}' ka stock kam hai")

            order.items.append(
                models.OrderItem(
                    menu_item_id=item.id,
                    quantity=line.quantity,
                    price_at_order=item.price,
                )
            )
            total += item.price * line.quantity

        order.total = total
        db.add(order)
        db.commit()                      # 3. Sab kuch ek saath permanent

    except IntegrityError:
        # Race condition: do requests ek saath aayi, doosri UNIQUE constraint se takrayi
        db.rollback()
        existing = _find_existing(db, user.id, idempotency_key)
        response.status_code = 200
        return existing
    except Exception:
        db.rollback()                    # koi bhi error: stock wapas, order nahi
        raise

    db.refresh(order)
    return order


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.scalar(select(models.User).where(models.User.email == email))
    order = db.get(models.Order, order_id)
    # Doosre user ka order bhi 404 dikhao (authorization, 4.4)
    if order is None or order.user_id != user.id:
        raise HTTPException(404, "Order not found")
    return order