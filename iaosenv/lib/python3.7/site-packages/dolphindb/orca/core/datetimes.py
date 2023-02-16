import itertools

import pandas as pd

from .common import default_session
from .internal import _ConstantSP


def _orca_unary_op(func, infered_ddb_dtypestr=None):
    # infered_ddb_dtypestr is used to convert Timestamp's data type
    # to make the category of two objects compatible
    @property
    def ufunc(self):
        return self._unary_op(func, infered_ddb_dtypestr)
    return ufunc


def _orca_logical_unary_op(func):
    @property
    def lufunc(self):
        return self._logical_unary_op(func)
    return lufunc


class Timestamp(object):
    
    def __init__(self, ts_input, freq=None, tz=None, unit=None, year=None, month=None, day=None, hour=None,
                 minute=None, second=None, microsecond=None, nanosecond=None, tzinfo=None, session=default_session()):
        if isinstance(ts_input, pd.Timestamp):
            data = ts_input
        else:
            data = pd.Timestamp(ts_input, freq, tz, unit, year, month, day, hour, minute, second, microsecond, nanosecond, tzinfo)
        self._session = session
        self._internal = data.to_datetime64()
        self._var = _ConstantSP.upload_obj(session, self._internal)

    @property
    def _var_name(self):
        return self._var._var_name

    def __repr__(self):
        return self._internal.__repr__()

    def __str__(self):
        return self._internal.__str__()


class DatetimeProperties(object):

    date = _orca_unary_op("date", "date")
    time = _orca_unary_op("second", "second")
    year = _orca_unary_op("year")
    month = _orca_unary_op("monthOfYear")
    day = _orca_unary_op("dayOfMonth")
    hour = _orca_unary_op("hour")
    minute = _orca_unary_op("minuteOfHour")
    hourminute = _orca_unary_op("minute", "minute")
    second = _orca_unary_op("secondOfMinute")
    microsecond = _orca_unary_op("(t->nanotimestamp(t).microsecond())")
    nanosecond = _orca_unary_op("(t->nanotimestamp(t).nanosecond()%1000)")    # TODO: nanosecond support other dtypes
    dayofyear = _orca_unary_op("dayOfYear")
    weekofyear = _orca_unary_op("weekOfYear")
    week = weekofyear
    dayofweek = _orca_unary_op("weekday{,false}")
    weekday = dayofweek
    quarter = _orca_unary_op("quarterOfYear")
    daysinmonth = _orca_unary_op("daysInMonth")
    days_in_month = daysinmonth

    is_month_start = _orca_logical_unary_op("isMonthStart")
    is_month_end = _orca_logical_unary_op("isMonthEnd")
    is_quarter_start = _orca_logical_unary_op("isQuarterStart")
    is_quarter_end = _orca_logical_unary_op("isQuarterEnd")
    is_year_start = _orca_logical_unary_op("isYearStart")
    is_year_end = _orca_logical_unary_op("isYearEnd")
    is_leap_year = _orca_logical_unary_op("isLeapYear")


class DatetimeMethods(DatetimeProperties):

    def __init__(self, s):
        self._s = s

    def _logical_unary_op(self, func):
        from .operator import BooleanExpression
        return BooleanExpression(self._s, None, func, 1)

    def _unary_op(self, func, infered_ddb_dtypestr):
        from .operator import ArithExpression
        return ArithExpression(self._s, None, func, 0,
                               infered_ddb_dtypestr=infered_ddb_dtypestr)

