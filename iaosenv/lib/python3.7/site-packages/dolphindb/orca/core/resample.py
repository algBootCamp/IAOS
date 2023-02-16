import abc
import itertools
from typing import Iterable

from pandas.tseries.frequencies import to_offset
from pandas.tseries.offsets import (
    FY5253, BDay, BMonthBegin, BMonthEnd, BQuarterBegin, BQuarterEnd,
    BYearBegin, BYearEnd, Day, FY5253Quarter, Hour, LastWeekOfMonth, Micro,
    Milli, Minute, MonthBegin, MonthEnd, Nano, QuarterBegin, QuarterEnd,
    Second, SemiMonthBegin, SemiMonthEnd, Week, WeekOfMonth, YearBegin,
    YearEnd)

from .groupby import GroupByOpsMixin
from .indexes import DatetimeIndex
from .internal import _ConstantSP, _InternalAccessor
from .operator import DataFrameLike, SeriesLike
from .utils import (_infer_level, _scale_nanos, check_key_existence,
                    dolphindb_temporal_types, sql_select)


class Resampler(_InternalAccessor, GroupByOpsMixin, metaclass=abc.ABCMeta):

    # week offset does not support nanos, use that of "7D" instead
    _DAY_NANOS = 86400000000000     # Day().nanos

    def __init__(self, session, internal, index, rule, on, level, where_expr, name,
                 groupkeys=[], sort=False,
                 offset=None, groupby_list=None, orderby_list=None, result_index_map=None,
                 contextby_result_index_map=None, min_time=None):
        self._session = session
        self._internal = internal
        self._index = index
        self._rule = rule
        self._where_expr = where_expr
        self._name = name
        self._groupkeys = groupkeys
        self._sort = True    # always order by resample column

        self._as_index = True
        self._ascending = True
        self._groupkeys = []
        self._min_time = None

        if (offset is not None and groupby_list is not None
                and orderby_list is not None and result_index_map is not None
                and contextby_result_index_map is not None):
            self._offset = offset
            self._groupby_list = groupby_list
            self._orderby_list = orderby_list
            self._result_index_map = result_index_map
            self._contextby_result_index_map = contextby_result_index_map
            self._min_time = min_time
            return

        if on is not None:
            if level is not None:
                raise ValueError("The Grouper cannot specify both a key and a level!")
            check_key_existence(on, self._data_columns)
            resample_column_name = on
        elif level is None:
            if not isinstance(self._index, DatetimeIndex):
                raise TypeError(f"Only valid with DatetimeIndex but got an "
                                f"instance of '{index.__class__.__name__}'")
            on = self._index_columns[0]
            resample_column_name = self._index_name
        elif isinstance(level, (str, int)):
            index_columns, _, index_names, _ = _infer_level(level, self._index_map)
            on = index_columns[0]
            resample_column_name = index_names[0]
            if self._ddb_dtypes[on] not in dolphindb_temporal_types:
                raise TypeError(f"Only valid with DatetimeIndex but got an "
                                f"instance of 'Index'")
        else:
            raise ValueError(f"The level {level} is not valid")

        self._offset = to_offset(rule)
        groupby_column = self._match_offset(self._offset, on)
        groupby_columns = groupkeys + [groupby_column]
        index_names = groupkeys + [resample_column_name]
        self._groupby_list, self._orderby_list, \
        self._result_index_map, self._contextby_result_index_map = \
            GroupByOpsMixin._get_groupby_list_orderby_list_and_index_map(
                groupby_columns, index_names, sort, resample=True)
        if not sort:
            self._orderby_list = self._orderby_list[-1:]

    @property
    @abc.abstractmethod
    def _is_series_like(self):
        pass

    @property
    @abc.abstractmethod
    def _is_dataframe_like(self):
        pass

    def __getitem__(self, key):
        if isinstance(key, str):
            klass = SeriesResampler
            name = key
        elif isinstance(key, Iterable):
            klass = DataFrameResampler
            name = self._name
        else:
            raise KeyError(key)
        new_odf = self._internal[key]
        return klass(self._session, new_odf, self._index, self._rule, None, None, self._where_expr, name,
                     self._groupkeys, self._sort, self._offset, self._groupby_list, self._orderby_list, self._result_index_map,
                     self._contextby_result_index_map, self._min_time)

    def _match_offset(self, offset, on):
        from .series import Series
        n = offset.n
        if on is None:
            if not isinstance(self._index, DatetimeIndex):
                raise TypeError(f"Only valid with DatetimeIndex but got an "
                                f"instance of '{self._index.__class__.__name__}'")
            col = self._index_columns[0]
        else:
            col = on
        ddb_dtype = self._ddb_dtypes[col]

        def get_min_time(offset, ddb_dtype, on):
            on_col = self._index_columns[0] if on is None else on
            script = sql_select([f"min({on_col})"], self._var_name, self._where_expr, is_exec=True)
            if isinstance(offset, (Day, Hour, Minute, Second, Milli, Micro, Nano)):
                nanos = _scale_nanos(offset.nanos, ddb_dtype) // offset.n
                script = f"bar(({script})[0], {nanos})"
            else:
                script = f"({script})[0]"
            self._min_time = _ConstantSP.run_script(self._session, script)
            return self._min_time.var_name

        if isinstance(offset, (Day, Milli, Nano)) and n == 1:
            if isinstance(offset, Day):
                key = f"date({col})"
            elif isinstance(offset, Milli):
                key = f"timestamp({col})"
            elif isinstance(offset, Nano):
                key = f"nanotimestamp({col})"
        else:
            min_time = get_min_time(offset, ddb_dtype, on)
            if isinstance(offset, (Day, Hour, Minute, Second, Milli, Micro, Nano)):
                nanos = _scale_nanos(offset.nanos, ddb_dtype)
                key = f"bar({col}-{min_time}, {nanos})+{min_time}"
            elif isinstance(offset, BDay):
                key = f"businessDay({col}, {min_time}, {n})"
            elif isinstance(offset, Week):
                weekday = offset.weekday
                day_nanos = _scale_nanos(self._DAY_NANOS, ddb_dtype)
                week_nanos = day_nanos * 7 * n
                if weekday is None:
                    offset1 = -1
                    offset2 = n * 7
                else:
                    offset1 = self._session.run(f"({min_time}+2-{weekday})%7-7")
                    offset2 = n*7 - offset1 - 1
                offset1_nanos = offset1 * day_nanos
                offset2_nanos = offset2 * day_nanos
                key = f"bar({col}-{min_time}+{offset1_nanos}, {week_nanos})+{min_time}+{offset2_nanos}"
            elif isinstance(offset, WeekOfMonth):
                week = offset.week
                weekday = offset.weekday
                key = f"weekOfMonth({col}, {week}, {weekday}, {min_time}, {n})"
            elif isinstance(offset, LastWeekOfMonth):
                weekday = offset.weekday
                key = f"lastWeekOfMonth({col}, {weekday}, {min_time}, {n})"
            elif isinstance(offset, MonthEnd):
                key = f"monthEnd({col}, {min_time}, {n})"
            elif isinstance(offset, MonthBegin):
                key = f"monthBegin({col}, {min_time}, {n})"
            elif isinstance(offset, BMonthEnd):
                key = f"businessMonthEnd({col}, {min_time}, {n})"
            elif isinstance(offset, BMonthBegin):
                key = f"businessMonthBegin({col}, {min_time}, {n})"
            elif isinstance(offset, SemiMonthEnd):
                day_of_month = offset.day_of_month
                key = f"semiMonthEnd({col}, {day_of_month}, {min_time}, {n})"
            elif isinstance(offset, SemiMonthBegin):
                day_of_month = offset.day_of_month
                key = f"semiMonthBegin({col}, {day_of_month}, {min_time}, {n})"
            elif isinstance(offset, QuarterEnd):
                starting_month = offset.startingMonth
                key = f"quarterEnd({col}, {starting_month}, {min_time}, {n})"
            elif isinstance(offset, QuarterBegin):
                starting_month = offset.startingMonth
                key = f"quarterBegin({col}, {starting_month}, {min_time}, {n})"
            elif isinstance(offset, BQuarterEnd):
                starting_month = offset.startingMonth
                key = f"businessQuarterEnd({col}, {starting_month}, {min_time}, {n})"
            elif isinstance(offset, BQuarterBegin):
                starting_month = offset.startingMonth
                key = f"businessQuarterBegin({col}, {starting_month}, {min_time}, {n})"
            elif isinstance(offset, YearEnd):
                month = offset.month
                key = f"yearEnd({col}, {month}, {min_time}, {n})"
            elif isinstance(offset, YearBegin):
                month = offset.month
                key = f"yearBegin({col}, {month}, {min_time}, {n})"
            elif isinstance(offset, BYearEnd):
                month = offset.month
                key = f"businessYearEnd({col}, {month}, {min_time}, {n})"
            elif isinstance(offset, BYearBegin):
                month = offset.month
                key = f"businessYearBegin({col}, {month}, {min_time}, {n})"
            elif isinstance(offset, FY5253):
                weekday = offset.weekday
                startingMonth = offset.startingMonth
                nearest = "true" if offset.variation == "nearest" else "false"
                key = f"fy5253({col}, {weekday}, {startingMonth}, {nearest}, {min_time}, {n})"
            elif isinstance(offset, FY5253Quarter):
                weekday = offset.weekday
                startingMonth = offset.startingMonth
                nearest = "true" if offset.variation == "nearest" else "false"
                qtr_with_extra_week = offset.qtr_with_extra_week
                key = f"fy5253Quarter({col}, {weekday}, {startingMonth}, {qtr_with_extra_week}, {nearest}, {min_time}, {n})"
            else:
                raise ValueError(f"Unsupported offset name {offset.name}")
        return key

    def _groupby_op(self, *args, **kwargs):
        return GroupByOpsMixin._groupby_op(self, *args, **kwargs)

    def _contextby_op(self, func, numeric_only):    # TODO: context by order
        if func in ("ffill", "bfill"):
            raise ValueError("Upsampling from level= or on= selection is not supported, use .set_index(...) to explicitly set index to datetime-like")
        select_list, _ = \
            self._generate_groupby_select_list_and_value_list(func, self._groupkeys, numeric_only)
        if len(select_list) == 0:
            raise NotImplementedError()
        contextby_list = (data_column for data_column, _ in self._contextby_result_index_map)
        select_list = itertools.chain(contextby_list, select_list)
        script = sql_select(select_list, self._var_name, self._where_expr,
                            groupby_list=self._groupby_list, is_groupby=False)
        return self._run_groupby_script(func, script, self._contextby_result_index_map)


class DataFrameResampler(DataFrameLike, Resampler):

    pass

class SeriesResampler(SeriesLike, Resampler):

    pass