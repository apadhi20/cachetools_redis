from cachetools.cache import Cache
import redis
import pickle


class RedisCache(Cache):
    """Extension of the Cache class to use redis as the key store."""

    def __init__(self, redis, namespace, max_keys=100):
        super().__init__(512, getsizeof=None)
        self.__redis = redis
        self.__namespace = namespace
        self.__max_keys = max_keys

    def __repr__(self):
        return "%s(namespace=%s, max_keys=%r)" % (self.__class__.__name__, self.__namespace,self.__max_keys,)

    def __getitem__(self, key):
        try:
            val = self.__redis.get(str(key))
            if val:
                return RedisCache.deserialize(val)
            else:
                raise KeyError()
        except KeyError:
            return self.__missing__(str(key))

    def __setitem__(self, key, value):
        while len(self) + 1 > self.__max_keys:
            self.popitem()

        self.__redis.set(str(key), RedisCache.serialize(value))

    def __delitem__(self, key):
        self.__redis.delete(str(key))

    def __contains__(self, key):
        return self.__redis.exists(str(key)) == 1

    def __missing__(self, key):
        raise KeyError(key)

    def __iter__(self):
        return self.__redis.scan_iter(match=self.__namespace + "*")

    def __len__(self):
        return len(self.__redis.keys(pattern=self.__namespace + "*"))

    def redis_key(self, *args, **kwargs):
        """Returns a key in the form of namespace:arg1:arg2..."""

        return ":".join([self.__namespace, *map(str, args)])

    def invalidateAll(self):
        for key in self:
            self.__redis.delete(key)

    def invalidate(self, key):
        """ Equivalent to del self[key] """
        del self[key]

    @staticmethod
    def deserialize(value):
        return pickle.loads(value)

    @staticmethod
    def serialize(value):
        return pickle.dumps(value)

    @property
    def max_keys(self):
        """The maximum number of keys to be stored in this cache."""
        return self.__max_keys
