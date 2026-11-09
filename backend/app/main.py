from fastapi import FastAPI, HTTPException
from fastapi import FastAPI, HTTPException, status
from app.schemas import MenuItem, MenuItemCreate, MenuItemUpdate

app = FastAPI(title="FoodOps API")

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


@app.post("/menu", response_model=MenuItem, status_code=status.HTTP_201_CREATED)
def create_menu_item(item: MenuItemCreate):
    global next_id
    new_item = {"id": next_id, **item.model_dump()}
    menu_items.append(new_item)
    next_id += 1
    return new_item


@app.get("/menu", response_model=list[MenuItem])
def list_menu_items():
    return menu_items


@app.get("/menu/{item_id}", response_model=MenuItem)
def get_menu_item(item_id: int):
    for item in menu_items:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Menu item not found")


@app.patch("/menu/{item_id}", response_model=MenuItem)
def update_menu_item(item_id: int, changes: MenuItemUpdate):
    for item in menu_items:
        if item["id"] == item_id:
            item.update(changes.model_dump(exclude_unset=True))
            return item
    raise HTTPException(status_code=404, detail="Menu item not found")


@app.delete("/menu/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(item_id: int):
    for i, item in enumerate(menu_items):
        if item["id"] == item_id:
            menu_items.pop(i)
            return
    raise HTTPException(status_code=404, detail="Menu item not found")