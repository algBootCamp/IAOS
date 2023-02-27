from db.myredis.redis_cli import RedisClient


class TestRedisClient:
    rc=RedisClient()
    def test_get_redis_cli(self):
        rcc=TestRedisClient.rc.get_redis_cli()
        rcc.set("test","test")
        print(rcc.get("test"))
