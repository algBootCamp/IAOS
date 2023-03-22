import time
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta


def test_time():
    now_time = time.localtime(time.time())
    this_year = now_time.tm_year
    this_month = now_time.tm_mon

    a = datetime(2012, 9, 23)
    print(a + timedelta(days=10))
    # 2012-10-03 00:00:00

    b = datetime(2012, 12, 21)
    d = b - a
    print(d.days)
    # 89

    now_m = datetime.today().month
    print(now_m)
    now_y = datetime.today().year
    print(now_y)
    print(this_year - 7)
    print(this_month - 4)
    sample_periods = 7
    shift_period = 13
    initial_date = datetime(now_y, now_m-1, 1)
    start_date = datetime(now_y - sample_periods, 1, 1)
    while start_date <= initial_date:
        print("start_date:"+str(start_date.year) + str(start_date.month).zfill(2) + str(start_date.day).zfill(2))
        end_date = start_date + relativedelta(months=+shift_period)
        if end_date>=initial_date:
            end_date=initial_date
        print("end_date:" + str(end_date.year) + str(end_date.month).zfill(2) + str(end_date.day).zfill(2))
        start_date=start_date + relativedelta(months=+shift_period)
