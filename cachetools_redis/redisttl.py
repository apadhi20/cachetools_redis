from .rediscache import RedisCache

import redis
from datetime import timedelta

class RedisTTL(RedisCache):
    """TTL Implementation Using Redis"""

    def __init__(self, ttl, namespace, max_keys, redis : redis.Redis):
        super().__init__(namespace=namespace, max_keys=max_keys, redis=redis)
        self.__ttl = ttl
        self.__redis = redis

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.__redis.expire(str(key), self.__ttl)

