import hashlib
import time
from collections import OrderedDict

_MAX_SIZE = 1000
_cache = OrderedDict()
_expiry = {}
_hits = 0
_misses = 0


def get_cache_key(audio_bytes: bytes, model_name: str = "") -> str:
    data = model_name.encode("utf-8") + audio_bytes
    return hashlib.sha256(data).hexdigest()


def get_cached_result(key: str) -> dict | None:
    global _hits, _misses
    if key not in _cache:
        _misses += 1
        return None
    if time.time() > _expiry[key]:
        del _cache[key]
        del _expiry[key]
        _misses += 1
        return None
    _cache.move_to_end(key)
    _hits += 1
    return _cache[key]


def cache_result(key: str, result: dict, ttl_seconds: int = 3600) -> None:
    if key in _cache:
        _cache.move_to_end(key)
    _cache[key] = result
    _expiry[key] = time.time() + ttl_seconds
    if len(_cache) > _MAX_SIZE:
        oldest_key, _ = _cache.popitem(last=False)
        _expiry.pop(oldest_key, None)


def get_cache_hits() -> int:
    return _hits


def get_cache_misses() -> int:
    return _misses