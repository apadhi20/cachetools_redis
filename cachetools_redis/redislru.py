import collections

from .rediscache import RedisCache
import redis

class RedisLRU(RedisCache):
    """Least Recently Used (LRU) cache implementation."""

    def __init__(self, namespace, max_keys, redis : redis.Redis):
        super().__init__(namespace=namespace, max_keys=max_keys, redis=redis)
        self.__order = collections.OrderedDict()
        self.__max_keys = max_keys

    def __repr__(self):
        return super().__repr__() + "  " + self.__order.__str__()

    def __getitem__(self, key):
        value = super().__getitem__(key)
        self.__update(key)
        return value

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.__update(key)

    def __delitem__(self, key):
        super().__delitem__(key)
        del self.__order[key]

    def popitem(self):
        """Remove and return the `(key, value)` pair least recently used."""
        try:
            key = next(iter(self.__order))
        except StopIteration:
            msg = '%s is empty' % self.__class__.__name__
            raise KeyError(msg) from None
        else:
            return (key, self.pop(key))

    def __update(self, key):
        try:
            self.__order.move_to_end(key)
        except KeyError:
            self.__order[key] = None

    def invalidateAll(self):
        super().invalidateAll()
        self.__order.clear()