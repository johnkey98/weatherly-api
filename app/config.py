"""Application configuration via environment variables (12-factor style)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="WEATHERLY_")
    app_name: str = "Weatherly API"
    app_version: str = "1.0.0"

    # OpenWeatherMap key. Leave empty to run in deterministic MOCK mode —
    # perfect for local dev, CI and demos without leaking keys.
    openweather_api_key: str = ""
    openweather_base_url: str = "https://api.openweathermap.org/data/2.5"

    # Cache TTL in seconds for upstream responses
    cache_ttl: int = 300

    # Rate limiting: requests per minute per client IP
    rate_limit_per_minute: int = 30

    request_timeout: float = 8.0


settings = Settings()
