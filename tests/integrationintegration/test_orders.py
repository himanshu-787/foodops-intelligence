from conftest import make_item


def order_body(item_id, qty):
    return {"items": [{"menu_item_id": item_id, "quantity": qty}]}


def stock_of(client, item_id):
    return client.get(f"/menu/{item_id}").json()["stock"]


def test_place_order_success(client, auth_headers):
    item = make_item(client, price=80, stock=3)
    res = client.post(
        "/orders",
        json=order_body(item, 2),
        headers={**auth_headers, "Idempotency-Key": "key-12345"},
    )
    assert res.status_code == 201
    assert res.json()["total"] == 160
    assert stock_of(client, item) == 1


def test_duplicate_request_does_not_create_second_order(client, auth_headers):
    item = make_item(client, stock=3)
    headers = {**auth_headers, "Idempotency-Key": "key-12345"}

    first = client.post("/orders", json=order_body(item, 2), headers=headers)
    second = client.post("/orders", json=order_body(item, 2), headers=headers)

    assert first.status_code == 201
    assert second.status_code == 200                 # naya nahi, purana wapas
    assert first.json()["id"] == second.json()["id"]
    assert stock_of(client, item) == 1               # sirf ek baar ghata


def test_insufficient_stock_returns_409(client, auth_headers):
    item = make_item(client, stock=1)
    res = client.post(
        "/orders",
        json=order_body(item, 2),
        headers={**auth_headers, "Idempotency-Key": "key-12345"},
    )
    assert res.status_code == 409
    assert stock_of(client, item) == 1


def test_failed_order_rolls_back_earlier_items(client, auth_headers):
    plenty = make_item(client, name="Dosa", stock=5)
    scarce = make_item(client, name="Idli", stock=1)
    body = {"items": [
        {"menu_item_id": plenty, "quantity": 2},
        {"menu_item_id": scarce, "quantity": 2},     # yeh fail hoga
    ]}
    res = client.post(
        "/orders", json=body,
        headers={**auth_headers, "Idempotency-Key": "key-12345"},
    )
    assert res.status_code == 409
    assert stock_of(client, plenty) == 5             # rollback: pehle item ka stock wapas


def test_order_requires_login(client):
    item = make_item(client)
    res = client.post(
        "/orders", json=order_body(item, 1),
        headers={"Idempotency-Key": "key-12345"},
    )
    assert res.status_code == 401


def test_invalid_quantity_rejected(client, auth_headers):
    item = make_item(client)
    res = client.post(
        "/orders", json=order_body(item, 0),
        headers={**auth_headers, "Idempotency-Key": "key-12345"},
    )
    assert res.status_code == 422


def test_invalid_status_transition_rejected(client, auth_headers):
    item = make_item(client)
    order = client.post(
        "/orders", json=order_body(item, 1),
        headers={**auth_headers, "Idempotency-Key": "key-12345"},
    ).json()
    res = client.patch(
        f"/orders/{order['id']}/status",
        json={"status": "DELIVERED"},
        headers=auth_headers,
    )
    assert res.status_code == 409


def test_cancel_restores_stock(client, auth_headers):
    item = make_item(client, stock=3)
    order = client.post(
        "/orders", json=order_body(item, 2),
        headers={**auth_headers, "Idempotency-Key": "key-12345"},
    ).json()
    assert stock_of(client, item) == 1

    client.patch(
        f"/orders/{order['id']}/status",
        json={"status": "CANCELLED"},
        headers=auth_headers,
    )
    assert stock_of(client, item) == 3


def test_my_orders_list(client, auth_headers):
    item = make_item(client, price=50, stock=5)
    client.post(
        "/orders",
        json=order_body(item, 1),
        headers={**auth_headers, "Idempotency-Key": "key-my-orders-1"},
    )
    res = client.get("/orders", headers=auth_headers)
    assert res.status_code == 200
    orders = res.json()
    assert len(orders) >= 1
    assert orders[0]["total"] == 50
