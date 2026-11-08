def calculate_total(prices: list[float], discount: float = 0.0) -> float:
    return sum(prices) * (1 - discount)


def find_item(menu: dict[str, int], name: str) -> int | None:
    return menu.get(name)       # item nahi mila toh None


print(calculate_total([250.0, 180.0], 0.1))
print(find_item({"dosa": 80}, "pizza"))      # None