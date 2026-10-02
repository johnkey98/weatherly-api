"""Weather endpoints with caching + rate limiting."""

from fastapi import APIRouter, HTTPException, Request

from ..cache import cache
from ..models import CurrentWeather, Forecast
from ..providers import fetch_current, fetch_forecast
from ..rate_limit import limiter

router = APIRouter(tags=["Weather"])


@router.get("/weather/{city}", response_model=CurrentWeather, summary="Current weather for a city")
async def current_weather(city: str, request: Request):
    limiter.check(request)
    key = f"current:{city.lower().strip()}"
    cached = cache.get(key)
    if cached:
        cached.cached = True
        return cached
    try:
        weather = await fetch_current(city)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=502, detail="Upstream weather provider unavailable")
    cache.set(key, weather)
    return weather


@router.get("/forecast/{city}", response_model=Forecast, summary="5-day forecast for a city")
async def forecast(city: str, request: Request):
    limiter.check(request)
    key = f"forecast:{city.lower().strip()}"
    cached = cache.get(key)
    if cached:
        cached.cached = True
        return cached
    try:
        result = await fetch_forecast(city)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=502, detail="Upstream weather provider unavailable")
    cache.set(key, result)
    return result
