def make_item(client, name="Dosa", price=80, stock=3):
    res = client.post("/menu", json={"name": name, "price": price, "stock": stock})
    return res.json()["id"]
