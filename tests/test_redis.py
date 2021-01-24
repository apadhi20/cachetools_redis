import pytest
from cachetools_redis import RedisTTL, RedisLRU
from datetime import timedelta
import time

def test_ttl(redis):
    r_ttl = RedisTTL(
        max_keys=256, 
        ttl=timedelta(seconds=3), 
        namespace="test_ttl", 
        redis=redis
    )

    key1 = r_ttl.redis_key("1")
    r_ttl[key1] = "1"

    assert r_ttl[key1] == RedisTTL.deserialize(redis.get(key1))
    assert r_ttl[key1] == "1"
    assert len(r_ttl) == 1

    time.sleep(1)

    key2 = r_ttl.redis_key("2")
    r_ttl[key2] = "2"

    assert r_ttl[key2] == RedisTTL.deserialize(redis.get(key2))
    assert r_ttl[key2] == "2"
    assert len(r_ttl) == 2

    time.sleep(2)

    assert not key1 in r_ttl
    assert len(r_ttl) == 1

    time.sleep(1)

    assert not key2 in r_ttl
    assert len(r_ttl) == 0

def test_ttl_invalidate(redis):
    r_ttl = RedisTTL(
        max_keys=256, 
        ttl=timedelta(seconds=60), 
        namespace="test_ttl_inv", 
        redis=redis
    )

    key1 = r_ttl.redis_key("1")
    r_ttl[key1] = RedisTTL.serialize("1")

    assert len(r_ttl) == 1

    del r_ttl[key1]

    assert len(r_ttl) == 0

    r_ttl[r_ttl.redis_key("1")] = "1"
    r_ttl[r_ttl.redis_key("2")] = "2"
    r_ttl[r_ttl.redis_key("3")] = "3"

    r_ttl.invalidateAll()

    assert len(r_ttl) == 0



def test_redis_lru(redis):
    r_lru = RedisLRU(
        max_keys=3, 
        namespace="test_lru", 
        redis=redis
    )

    assert repr(r_lru) is not None
    assert r_lru.max_keys == 3

    key1 = r_lru.redis_key("1-1")

    with pytest.raises(KeyError):
        for x in range(3):
            encoded_x = RedisLRU.serialize(x)
            redis.set(r_lru.redis_key(x), encoded_x)

        r_lru[key1] = "1"

    r_lru.invalidateAll()
    assert len(r_lru) == 0

    r_lru[key1] = "1"

    assert r_lru[key1] == RedisLRU.deserialize(redis.get(key1))

    key2 = r_lru.redis_key("2-1")
    r_lru[key2] = "2"

    assert r_lru[key2] == RedisLRU.deserialize(redis.get(key2))
    assert r_lru[key2] == "2"
    assert len(r_lru) == 2

    for x in range(1, 30):
        r_lru[r_lru.redis_key(str(x))] = x
        assert len(r_lru) == 3

    assert r_lru.redis_key("27") in r_lru
    assert r_lru.redis_key("28") in r_lru
    assert r_lru.redis_key("29") in r_lru

    r_lru.invalidate(r_lru.redis_key("29"))
    assert len(r_lru) == 2
    assert r_lru.redis_key("29") not in r_lru

    with pytest.raises(KeyError):
        r_lru[r_lru.redis_key("29")]

    r_lru.invalidateAll()
    assert len(r_lru) == 0
