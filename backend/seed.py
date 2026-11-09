import random

from app import models
from app.database import Base, SessionLocal, engine

Base.metadata.create_all(bind=engine)

cuisines = ["Mughlai", "South Indian", "Italian", "Chinese", "Cafe"]
words = ["Biryani", "Dosa", "Pizza", "Noodles", "Coffee", "Thali", "Kebab"]

db = SessionLocal()
for i in range(200):
    cuisine = random.choice(cuisines)
    db.add(models.Restaurant(
        name=f"{random.choice(words)} House {i}",
        cuisine=cuisine,
        rating=round(random.uniform(2.5, 5.0), 1),
        is_veg=(cuisine == "South Indian"),
    ))
db.commit()
db.close()
print("200 restaurants add ho gaye")