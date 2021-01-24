import pytest
from redis import Redis

@pytest.fixture
def redis():
    redis_db = Redis(host="localhost", port="6379", db=0, encoding="utf-8", decode_responses=False)
    assert redis_db.ping()
    
    return redis_db
