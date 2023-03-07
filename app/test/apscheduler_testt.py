# 导入后台调度模块
from apscheduler.schedulers.background import BackgroundScheduler
# 导入时间模块
import time


# job1任务
def job1():
    print('我是job1，我每3秒执行一次')


# 主程序
def main():
    while (True):
        print('我是主程序，我每1秒执行一次')
        # 休息一秒
        time.sleep(1)


# 入口函数
if __name__ == '__main__':
    # 实例一个后台调度
    scheduler = BackgroundScheduler(timezone='Asia/Shanghai')
    # 后台调度添加一个任务，每3秒执行一次
    # date：指定日期执行
    # interval：可以指定具体间隔多少时间执行一次
    # cron：可以指定执行的日期策略（最强大）
    # scheduler.add_job(job1, 'interval', id='3_second_job', seconds=3)
    # 在2022年1月1日-2023年1月1日间的每周一到周五的6点6分执行
    scheduler.add_job(job1, 'cron', day_of_week='mon-fri', hour=22, minute=47, start_date='2022-1-1',
                      end_date='2024-1-1')
    # 开始执行调度
    scheduler.start()
    # 主程序
    main()
