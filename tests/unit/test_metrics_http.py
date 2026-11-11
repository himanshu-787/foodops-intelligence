from fastapi.testclient import TestClient
from prometheus_client import REGISTRY

from app.main import app


def val(name, labels):
    return REGISTRY.get_sample_value(name, labels) or 0.0


def test_request_is_counted_with_route_template():
    labels = {"method": "GET", "path": "/health", "status": "200"}
    before = val("foodops_http_requests_total", labels)
    TestClient(app).get("/health")
    assert val("foodops_http_requests_total", labels) == before + 1


def test_unknown_paths_do_not_explode_cardinality():
    labels = {"method": "GET", "path": "unmatched", "status": "404"}
    before = val("foodops_http_requests_total", labels)
    c = TestClient(app)
    c.get("/no-such-route-111")
    c.get("/no-such-route-222")
    assert val("foodops_http_requests_total", labels) == before + 2
    assert "no-such-route" not in c.get("/metrics").text


def test_metrics_endpoint_text_format():
    r = TestClient(app).get("/metrics")
    assert r.status_code == 200
    assert "foodops_http_requests_total" in r.text
    assert r.headers["content-type"].startswith("text/plain")


def test_metrics_token_enforced_when_set(monkeypatch):
    monkeypatch.setenv("METRICS_TOKEN", "s3cret")
    c = TestClient(app)
    assert c.get("/metrics").status_code == 401
    assert c.get("/metrics", headers={"Authorization": "Bearer wrong"}).status_code == 401
    assert c.get("/metrics", headers={"Authorization": "Bearer s3cret"}).status_code == 200
