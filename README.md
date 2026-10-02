# 🌤️ Weatherly API — Production-Minded Weather Microservice

![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/Python-3.12-3776ab?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-ready-2496ed?logo=docker&logoColor=white)

Weatherly is a weather microservice that demonstrates how production APIs are actually engineered: **TTL response caching** (configurable, with live hit-rate metrics), **per-IP sliding-window rate limiting** with proper `429` + `Retry-After` semantics, **Pydantic response contracts** on every endpoint, **layered architecture** (providers / cache / limiter / routers), and a full **pytest suite that runs with zero network access**.

The clever part: with an `OpenWeatherMap` key it serves **live** data; without one it serves **deterministic mock data** seeded per city+day — so the API, docs, and tests all work in demos and CI without a single credential or network call. Interactive Swagger docs are generated automatically at `/docs`.

## ✨ Features

- **`GET /weather/{city}`** — current conditions (temp, feels-like, humidity, pressure, wind) with 5-minute caching.
- **`GET /forecast/{city}`** — 5-day forecast with daily min/max and precipitation probability, collapsed from 3-hour upstream steps.
- **Dual mode** — `live` (real OpenWeatherMap data) or `mock` (deterministic, seeded, offline).
- **Rate limiting** — 30 req/min per IP by default, sliding window, `Retry-After` header on 429.
- **TTL cache** — in-process, atomic entries, exposed hit-rate in `/health`.
- **Typed errors** — `404` unknown city, `502` upstream failure, `422` validation, all machine-readable.
- **Docker** — slim image, non-root user, built-in `HEALTHCHECK`.
- **Tests** — 6 pytest cases covering contracts, caching behavior, forecast integrity and rate-limit triggering.

## 🚀 Getting Started

```bash
git clone https://github.com/johnkey98/weatherly-api.git
cd weatherly-api

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload
# → http://localhost:8000  (docs: http://localhost:8000/docs)
```

No API key needed for the first run — mock mode is the default.

### Live mode

```bash
export WEATHERLY_OPENWEATHER_API_KEY=your-key   # free tier is fine
uvicorn app.main:app --reload                   # now serves real data
```

### Docker

```bash
docker build -t weatherly .
docker run -p 8000:8000 -e WEATHERLY_OPENWEATHER_API_KEY=$KEY weatherly
```

### Tests

```bash
pytest -v
```

## 📡 API Reference

| Method | Endpoint          | Description                                     | Errors      |
| ------ | ----------------- | ----------------------------------------------- | ----------- |
| GET    | `/weather/{city}` | Current weather (cached 300s)                   | 404, 429, 502 |
| GET    | `/forecast/{city}`| 5-day forecast (cached 300s)                    | 404, 429, 502 |
| GET    | `/health`         | Status, mode, cache stats                       | –           |

### Example

```bash
curl http://localhost:8000/weather/tehran
```

```json
{
  "city": "Tehran",
  "country": "--",
  "temperature": 24.0,
  "feels_like": 25.5,
  "humidity": 41,
  "pressure": 1012,
  "wind_speed": 3.6,
  "condition": "Clear",
  "description": "clear sky",
  "source": "mock",
  "cached": false
}
```

## ⚙️ Configuration (env vars, prefix `WEATHERLY_`)

| Variable                | Default     | Meaning                              |
| ----------------------- | ----------- | ------------------------------------ |
| `OPENWEATHER_API_KEY`   | *(empty)*   | Empty = deterministic mock mode      |
| `CACHE_TTL`             | `300`       | Cache seconds per response           |
| `RATE_LIMIT_PER_MINUTE` | `30`        | Sliding-window requests per IP       |
| `REQUEST_TIMEOUT`       | `8.0`       | Upstream timeout in seconds          |

## 📂 Project Structure

```
weatherly-api/
├── app/
│   ├── main.py          # FastAPI app factory + /health
│   ├── config.py        # pydantic-settings configuration
│   ├── models.py        # Pydantic response contracts
│   ├── providers.py     # OpenWeatherMap client + mock generator
│   ├── cache.py         # TTL cache with hit/miss stats
│   ├── rate_limit.py    # Sliding-window limiter
│   └── routers/weather.py
├── tests/test_api.py    # Offline pytest suite
├── Dockerfile
└── requirements.txt
```

## 🗺 Roadmap

- [ ] Redis cache backend for horizontal scaling
- [ ] API-key auth for public deployments
- [ ] Prometheus metrics endpoint
- [ ] Async batch endpoint (`/weather?cities=a,b,c`)

## 📄 License

[MIT](LICENSE) © [John Key](https://github.com/johnkey98)
