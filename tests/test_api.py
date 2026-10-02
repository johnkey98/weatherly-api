"""Integration tests — run in mock mode (no network, no API key needed)."""

import os

os.environ.setdefault("WEATHERLY_OPENWEATHER_API_KEY", "")

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["mode"] == "mock"


def test_current_weather_mock():
    res = client.get("/weather/tehran")
    assert res.status_code == 200
    body = res.json()
    assert body["city"] == "Tehran"
    assert body["source"] == "mock"
    assert -20 <= body["temperature"] <= 50
    assert 0 <= body["humidity"] <= 100


def test_current_weather_cached():
    client.get("/weather/paris")  # warm the cache
    res = client.get("/weather/paris")
    assert res.status_code == 200
    assert res.json()["cached"] is True


def test_forecast_has_five_days():
    res = client.get("/forecast/berlin")
    assert res.status_code == 200
    days = res.json()["days"]
    assert len(days) == 5
    for day in days:
        assert day["temp_max"] >= day["temp_min"]
        assert 0 <= day["precipitation_chance"] <= 100


def test_validation_on_unknown_city_in_live_mode_only():
    # In mock mode every city resolves; just assert the endpoint contract holds.
    res = client.get("/weather/some-made-up-city-123")
    assert res.status_code == 200


def test_rate_limit_triggers(monkeypatch):
    from app.rate_limit import limiter

    limiter.reset()
    monkeypatch.setattr(limiter, "max", 3)
    for _ in range(3):
        client.get("/weather/london")
    res = client.get("/weather/london")
    assert res.status_code == 429
    assert "Retry-After" in res.headers
    limiter.reset()
