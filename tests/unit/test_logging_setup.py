import json
import logging

from fastapi.testclient import TestClient

from app.logging_setup import JsonFormatter, request_id_var, setup_logging
from app.main import app


def test_json_formatter_emits_valid_json_with_request_id():
    token = request_id_var.set("req-12345678")
    try:
        rec = logging.LogRecord("foodops.t", logging.INFO, __file__, 1, "hello %s", ("world",), None)
        out = json.loads(JsonFormatter().format(rec))
    finally:
        request_id_var.reset(token)
    assert out["msg"] == "hello world"
    assert out["level"] == "INFO" and out["request_id"] == "req-12345678"


def test_request_id_generated_echoed_and_untrusted_input_replaced():
    c = TestClient(app)
    generated = c.get("/health").headers["x-request-id"]
    assert len(generated) == 16

    good = c.get("/health", headers={"X-Request-ID": "abc12345-req"})
    assert good.headers["x-request-id"] == "abc12345-req"

    bad = c.get("/health", headers={"X-Request-ID": "x" * 200})  # bahut lamba
    assert bad.headers["x-request-id"] != "x" * 200
    bad2 = c.get("/health", headers={"X-Request-ID": "bad id with spaces!!"})
    assert " " not in bad2.headers["x-request-id"]


def test_setup_logging_is_idempotent():
    setup_logging()
    setup_logging()
    root = logging.getLogger()
    assert sum(isinstance(h.formatter, JsonFormatter) for h in root.handlers) == 1
