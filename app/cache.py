"""In-memory TTL cache with graceful expiry and stats."""

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Entry:
    value: Any
    expires_at: float


@dataclass
class TTLCache:
    ttl: float = 300
    _store: dict = field(default_factory=dict)
    hits: int = 0
    misses: int = 0

    def get(self, key: str):
        entry = self._store.get(key)
        if entry is None:
            self.misses += 1
            return None
        if entry.expires_at < time.time():
            del self._store[key]
            self.misses += 1
            return None
        self.hits += 1
        return entry.value

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        self._store[key] = Entry(value=value, expires_at=time.time() + (ttl if ttl is not None else self.ttl))

    def clear(self) -> None:
        self._store.clear()

    @property
    def size(self) -> int:
        return len(self._store)


cache = TTLCache()
