"""Upstream weather providers: OpenWeatherMap client + deterministic mock."""

import hashlib
import random
from datetime import date, timedelta

import httpx

from .config import settings
from .models import CurrentWeather, Forecast, ForecastDay

CONDITIONS = ["Clear", "Clouds", "Rain", "Snow", "Thunderstorm"]
DESCRIPTIONS = {
    "Clear": "clear sky",
    "Clouds": "scattered clouds",
    "Rain": "moderate rain",
    "Snow": "light snow",
    "Thunderstorm": "thunderstorm with rain",
}


async def fetch_current(city: str) -> CurrentWeather:
    """Return current weather — live from OpenWeatherMap when a key is set, else mock."""
    if not settings.openweather_api_key:
        return _mock_current(city)

    async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
        resp = await client.get(
            f"{settings.openweather_base_url}/weather",
            params={"q": city, "appid": settings.openweather_api_key, "units": "metric"},
        )
        if resp.status_code == 404:
            raise LookupError(f"City '{city}' not found")
        resp.raise_for_status()
        data = resp.json()

    return CurrentWeather(
        city=data["name"],
        country=data.get("sys", {}).get("country", ""),
        temperature=data["main"]["temp"],
        feels_like=data["main"]["feels_like"],
        humidity=data["main"]["humidity"],
        pressure=data["main"]["pressure"],
        wind_speed=data.get("wind", {}).get("speed", 0.0),
        condition=data["weather"][0]["main"],
        description=data["weather"][0]["description"],
        source="openweathermap",
    )


async def fetch_forecast(city: str) -> Forecast:
    """5-day forecast — live when configured, else mock."""
    if not settings.openweather_api_key:
        return _mock_forecast(city)

    async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
        resp = await client.get(
            f"{settings.openweather_base_url}/forecast",
            params={"q": city, "appid": settings.openweather_api_key, "units": "metric"},
        )
        if resp.status_code == 404:
            raise LookupError(f"City '{city}' not found")
        resp.raise_for_status()
        data = resp.json()

    # OpenWeather gives 3-hour steps — collapse to daily min/max
    daily: dict[str, dict] = {}
    for point in data["list"]:
        day = point["dt_txt"][:10]
        bucket = daily.setdefault(day, {"max": -99, "min": 99, "condition": point["weather"][0]["main"], "pop": 0})
        bucket["max"] = max(bucket["max"], point["main"]["temp_max"])
        bucket["min"] = min(bucket["min"], point["main"]["temp_min"])
        bucket["pop"] = max(bucket["pop"], round(point.get("pop", 0) * 100))

    return Forecast(
        city=data["city"]["name"],
        country=data["city"].get("country", ""),
        days=[
            ForecastDay(date=d, temp_max=v["max"], temp_min=v["min"], condition=v["condition"], precipitation_chance=v["pop"])
            for d, v in sorted(daily.items())[:5]
        ],
        source="openweathermap",
    )


# ------------------------------ mock mode ------------------------------ #

def _seed(city: str) -> random.Random:
    """Deterministic pseudo-weather per city+day, so demos are stable."""
    digest = hashlib.sha256(f"{city.lower()}:{date.today().isoformat()}".encode()).hexdigest()
    return random.Random(int(digest[:12], 16))


def _mock_current(city: str) -> CurrentWeather:
    rng = _seed(city)
    condition = rng.choice(CONDITIONS)
    base = rng.randint(2, 34)
    return CurrentWeather(
        city=city.title(),
        country="--",
        temperature=float(base),
        feels_like=float(base + rng.randint(-3, 3)),
        humidity=rng.randint(25, 95),
        pressure=rng.randint(995, 1030),
        wind_speed=round(rng.uniform(0.5, 12.0), 1),
        condition=condition,
        description=DESCRIPTIONS[condition],
        source="mock",
    )


def _mock_forecast(city: str) -> Forecast:
    rng = _seed(city)
    days = []
    for offset in range(5):
        day = date.today() + timedelta(days=offset)
        condition = rng.choice(CONDITIONS)
        tmax = rng.randint(8, 35)
        days.append(
            ForecastDay(
                date=day.isoformat(),
                temp_max=float(tmax),
                temp_min=float(tmax - rng.randint(4, 12)),
                condition=condition,
                precipitation_chance=rng.randint(0, 90),
            )
        )
    return Forecast(city=city.title(), country="--", days=days, source="mock")
