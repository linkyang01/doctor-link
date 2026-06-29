_cache = {}

def get(key):
    return _cache.get(key)  # BUG: no null-cache / bloom filter

def set(key, value, ttl=300):
    _cache[key] = value  # BUG: ignores ttl
