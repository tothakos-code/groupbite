import threading
from abc import ABC, abstractmethod
from typing import Optional


class BundleCache(ABC):
    @abstractmethod
    def get(self, order_id: int) -> Optional[dict]:
        pass

    @abstractmethod
    def set(self, order_id: int, result: dict) -> None:
        pass

    @abstractmethod
    def invalidate(self, order_id: int) -> None:
        pass


class InProcessBundleCache(BundleCache):
    def __init__(self):
        self._lock = threading.Lock()
        self._store: dict[int, dict] = {}

    def get(self, order_id: int) -> Optional[dict]:
        with self._lock:
            return self._store.get(order_id)

    def set(self, order_id: int, result: dict) -> None:
        with self._lock:
            self._store[order_id] = result

    def invalidate(self, order_id: int) -> None:
        with self._lock:
            self._store.pop(order_id, None)


class RedisBundleCache(BundleCache):
    def get(self, order_id: int) -> Optional[dict]:
        raise NotImplementedError("RedisBundleCache is not yet implemented")

    def set(self, order_id: int, result: dict) -> None:
        raise NotImplementedError("RedisBundleCache is not yet implemented")

    def invalidate(self, order_id: int) -> None:
        raise NotImplementedError("RedisBundleCache is not yet implemented")


_inprocess_cache = InProcessBundleCache()


def get_bundle_cache() -> BundleCache:
    try:
        from flask import current_app
        backend = current_app.config.get("BUNDLE_CACHE_BACKEND", "inprocess")
    except RuntimeError:
        backend = "inprocess"
    if backend == "redis":
        return RedisBundleCache()
    return _inprocess_cache
