"""Weatherly API — FastAPI application factory."""

from fastapi import FastAPI

from .cache import cache
from .config import settings
from .routers import weather

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Production-minded weather microservice: TTL caching, per-IP rate limiting, "
        "Pydantic response contracts and interactive docs. Runs in live mode with an "
        "OpenWeatherMap key, or deterministic mock mode without one."
    ),
)

app.include_router(weather.router)


@app.get("/health", response_model=dict, tags=["System"], summary="Health check")
async def health():
    total = cache.hits + cache.misses
    return {
        "status": "ok",
        "version": settings.app_version,
        "mode": "live" if settings.openweather_api_key else "mock",
        "cache_entries": cache.size,
        "cache_hit_rate": round(cache.hits / total, 3) if total else 0.0,
    }
