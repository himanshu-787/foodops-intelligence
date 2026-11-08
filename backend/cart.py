def calculate_total(cart, discount_threshold=500):
    total = sum(cart)
    if total > discount_threshold:
        total = total * 0.9
    return total


def most_expensive_item(menu):
    return max(menu, key=menu.get)


def cheap_items(menu, limit=100):
    return {name: price for name, price in menu.items() if price < limit}


if __name__ == "__main__":
    print(calculate_total([250, 180, 120]))
    print(most_expensive_item({"dosa": 80, "idli": 40, "vada": 30}))
    print(cheap_items({"dosa": 80, "idli": 40, "vada": 30}, 50))