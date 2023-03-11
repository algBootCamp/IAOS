from db.myredis.redis_cli import RedisClient
from util.obj_util import loads_data


class TestRedisClient:
    rc = RedisClient()

    def test_get_redis_cli(self):
        rcc = TestRedisClient.rc.get_redis_cli()
        # rcc.set("test","test")
        # print(rcc.get("test"))
        print(loads_data(rcc.get("base_stock_infos")))

    def test_get_redis(self):
        rcc = TestRedisClient.rc.get_redis_cli()
        print(int(rcc.get("RemoteBasicDataCache.updateflag")) == 1)
