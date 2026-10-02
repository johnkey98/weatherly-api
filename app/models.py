"""Pydantic response models — the API contract."""

from typing import Literal

from pydantic import BaseModel, Field


class CurrentWeather(BaseModel):
    city: str
    country: str
    temperature: float = Field(description="Celsius")
    feels_like: float
    humidity: int = Field(ge=0, le=100)
    pressure: int
    wind_speed: float = Field(description="m/s")
    condition: str
    description: str
    source: Literal["openweathermap", "mock"]
    cached: bool = False


class ForecastDay(BaseModel):
    date: str
    temp_max: float
    temp_min: float
    condition: str
    precipitation_chance: int = Field(ge=0, le=100)


class Forecast(BaseModel):
    city: str
    country: str
    days: list[ForecastDay]
    source: Literal["openweathermap", "mock"]
    cached: bool = False


class Health(BaseModel):
    status: str
    version: str
    mode: str
    cache_entries: int
    cache_hit_rate: float
