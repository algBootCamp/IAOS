import threading
import time

from db.myredis.redis_lock import RedisLock


def test_lock():
    # 线程模拟进程
    a1 = threading.Thread(target=run_work, args=("user-1",))
    a2 = threading.Thread(target=run_work, args=("user-2",))

    a1.start()
    a2.start()


def run_work(my_user_id):
    r = RedisLock(lock_name="test-res", uid=my_user_id, expire=5)
    try:
        if r.lock():
            print(f"working ,{my_user_id} 获得锁")
            time.sleep(20)
        else:
            print(f"quit, {my_user_id} 未获得锁")
    finally:
        r.unlock()
