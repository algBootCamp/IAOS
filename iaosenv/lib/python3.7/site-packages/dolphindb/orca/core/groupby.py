import abc
import itertools
from typing import Iterable

from .indexes import Index
from .internal import _InternalAccessor
from .merge import MergeExpression
from .operator import (ArithExpression, BooleanExpression, DataFrameLike,
                       SeriesLike, StatOpsMixin)
from .series import Series
from .utils import (ORCA_INDEX_NAME_FORMAT, _infer_level,
                    _unsupport_columns_axis, check_key_existence,
                    dolphindb_numeric_types, get_orca_obj_from_script,
                    sql_select, to_dolphindb_literal)


def _orca_groupby_op(func, numeric_only):
    def gfunc(self):
        return self._groupby_op(func, numeric_only)
    return gfunc


def _orca_contextby_op(func, numeric_only):
    def cfunc(self):
        return self._contextby_op(func, numeric_only)
    return cfunc


class GroupByOpsMixin(metaclass=abc.ABCMeta):

    all = _orca_groupby_op("all", numeric_only=False)
    any = _orca_groupby_op("any", numeric_only=False)
    count = _orca_groupby_op("count", numeric_only=False)
    size = _orca_groupby_op("size", numeric_only=False)
    sum = _orca_groupby_op("sum", numeric_only=True)
    sum2 = _orca_groupby_op("sum2", numeric_only=True)
    prod = _orca_groupby_op("prod", numeric_only=True)
    mean = _orca_groupby_op("mean", numeric_only=True)
    median = _orca_groupby_op("median", numeric_only=True)
    min = _orca_groupby_op("min", numeric_only=False)
    max = _orca_groupby_op("max", numeric_only=False)
    std = _orca_groupby_op("std", numeric_only=True)
    var = _orca_groupby_op("var", numeric_only=True)
    sem = _orca_groupby_op("sem", numeric_only=True)
    mad = _orca_groupby_op("mad", numeric_only=True)
    skew = _orca_groupby_op("skew", numeric_only=True)
    kurtosis = _orca_groupby_op("kurtosis", numeric_only=True)
    first = _orca_groupby_op("first", numeric_only=False)
    last = _orca_groupby_op("last", numeric_only=False)

    ohlc = _orca_groupby_op("ohlc", numeric_only=True)

    # context by ops
    ffill = _orca_contextby_op("ffill", numeric_only=False)
    pad = ffill
    bfill = _orca_contextby_op("bfill", numeric_only=False)
    backfill = bfill
    cumcount = _orca_contextby_op("cumcount", numeric_only=False)
    cummax = _orca_contextby_op("cummax", numeric_only=False)
    cummin = _orca_contextby_op("cummin", numeric_only=False)
    cumprod = _orca_contextby_op("cumprod", numeric_only=True)
    cumsum = _orca_contextby_op("cumsum", numeric_only=True)
    pct_change = _orca_contextby_op("percentChange", numeric_only=True)

    def diff(self, periods=1, axis=0):
        _unsupport_columns_axis(self, axis)
        if periods != 1:
            raise ValueError("periods must be 1")
        return self._contextby_op("deltas", numeric_only=True)

    def shift(self, periods=1, freq=None, axis=0, fill_value=None):
        _unsupport_columns_axis(self, axis)

        if not isinstance(periods, int):
            raise TypeError("periods must be an integer")
        return self._contextby_op(f"move{{,{periods}}}", numeric_only=False)
        # TODO: fill_value
        # if fill_value is not None:
        #     return expr.fillna(fill_value)
        # else:
        #     return expr

    _STRING_TO_NUMERIC_ONLY = {
        "all": False,
        "any": False,
        "count": False,
        "size": False,
        "sum": True,
        "sum2": True,
        "prod": True,
        "mean": True,
        "median": True,
        "min": False,
        "max": False,
        "std": True,
        "var": True,
        "sem": True,
        "med": True,
        "skew": True,
        "kurtosis": True,
        "first": False,
        "last": False,

        "ohlc": True,

        "bfill": False,
        "ffill": False,
        "cumcount": False,
        "cummax": False,
        "cummin": False,
        "cumprod": True,
        "cumsum": True,
        "pct_change": True,
        "diff": True,
    }

    def rank(self, axis=0, method='min', na_option='keep', ascending=True, pct=False, rank_from_zero=False, group_num=None):
        from .operator import _check_rank_arguments
        func = _check_rank_arguments(axis, method, na_option, ascending, pct, rank_from_zero, group_num)
        return self._contextby_op(func, numeric_only=False)

    def ols(self, y, x, column_names, intercept=True):
        y, _ = check_key_existence(y, self._data_columns)
        x, _ = check_key_existence(x, self._data_columns)
        if len(y) != 1:
            raise ValueError("y must be a single column")
        y_script = y[0]
        x_script = ",".join(x)
        intercept = "true" if intercept else "false"
        column_names_literal = to_dolphindb_literal(column_names)

        script = f"ols({y_script}, ({x_script}), {intercept}) as {column_names_literal}"
        orderby_list = self._orderby_list if self._sort else None

        script = sql_select([script], self._var_name, self._where_expr,
                            groupby_list=self._groupby_list, orderby_list=orderby_list,
                            asc=self._ascending)
        return self._run_groupby_script("ols", script, self._result_index_map)

    def aggregate(self, func, *args, **kwargs):
        return self._groupby_op(func, False)

    agg = aggregate

    def apply(self, func, *args, **kwargs):
        # if not isinstance(func, str):
        #     raise ValueError("Orca does not support callable func; func must be a string representing a DolphinDB function")
        return self._groupby_op(func, numeric_only=False)

    def transform(self, func="", *args, **kwargs):
        # if not isinstance(func, str):
        #     raise ValueError("Orca does not support callable func; func must be a string representing a DolphinDB function")
        return self._contextby_op(func, False)

    @staticmethod
    def _get_groupby_list_orderby_list_and_index_map(groupby_columns, index_names, sort, resample):
        index_columns = [ORCA_INDEX_NAME_FORMAT(i) for i in range(len(index_names))]
        groupby_list = [f"{groupby_column} as {index_column}"
                        for groupby_column, index_column in zip(groupby_columns, index_columns)]
        if sort:
            orderby_list = index_columns
        elif resample:
            orderby_list = index_columns[-1:]
        else:
            orderby_list = None 
        index_map = [(index_column, None) if index_name is None
                     else (index_column, (index_name,))
                     for index_name, index_column in zip(index_names, index_columns)]
        contextby_index_map = [(index_column, None) if index_name is None
                               else (index_name, (index_name,))
                               for index_name, index_column in zip(index_names, index_columns)]
        return groupby_list, orderby_list, index_map, contextby_index_map

    def _generate_groupby_select_list_and_value_list(self, func, groupkeys, numeric_only):
        def check_func_existance(func):
            return self._STRING_TO_NUMERIC_ONLY.get(func, False)

        def ohlc_select_list(select_col, col):
            return [f"first({select_col}) as {col}_open",
                    f"max({select_col}) as {col}_high",
                    f"min({select_col}) as {col}_low",
                    f"last({select_col}) as {col}_close"]

        def funcname_alias(func):
            ALIAS = {"pad": "ffill", "backfill": "bfill", "pct_change": "percentChange", "diff": "deltas"}
            return ALIAS.get(func, func)

        select_columns = self._get_data_select_list()
        data_columns = self._data_columns
        # special functions
        if func == "size" or func is len:
            return ["count(*)"], []
        if func == "ohlc":
            column_ohlcs = (ohlc_select_list(select_col, col)
                            for select_col, col in zip(select_columns, data_columns))
            return list(itertools.chain(*column_ohlcs)), []

        if isinstance(func, str):
            func = funcname_alias(func)
            numeric_only = check_func_existance(func)
        elif isinstance(func, list):
            select_list = []
            func_names = []
            for func_name in func:
                if not isinstance(func_name, str):
                    raise TypeError(f"Only strings are supported to be used as function names")
                func_names.append(funcname_alias(func_name))
            select_list= ([f"{func_name}({col}) as {col}_{func_name}" for func_name in func_names]
                          for col in select_columns if col not in groupkeys)
            select_list = list(itertools.chain(*select_list))
            return select_list, []
        elif isinstance(func, dict):
            select_list = []
            for col, func_name in func.items():
                if not isinstance(func_name, str):
                    raise TypeError(f"Only strings are supported to be used as function names")
                try:
                    col_idx = data_columns.index(col)
                except ValueError:
                    raise KeyError(col)
                func_name = funcname_alias(func_name)
                # check_func_existance(func_name)
                select_col = select_columns[col_idx]
                if func_name == "ohlc":
                    select_list.extend(ohlc_select_list(select_col, col))
                else:
                    select_list.append(f"{func_name}({select_col}) as {col}")
            return select_list, []
        else:
            from orca.converter.dolphindb_parser import parse_py_code_to_dolphindb_code
            func_script = parse_py_code_to_dolphindb_code(func)
            raise NotImplementedError

        # is_op_on_different_columns = False
        if isinstance(self._internal, (ArithExpression, BooleanExpression)):
            numeric_only = False
        ddb_dtypes = self._ddb_dtypes
        select_list = []
        value_list = []
        for select_col, col in zip(select_columns, data_columns):
            if (col not in groupkeys
                    and (not numeric_only
                        or ddb_dtypes[col] in dolphindb_numeric_types)):
                select_list.append(f"{func}({select_col}) as {col}")
                value_list.append(f"{func}({select_col})")
        return select_list, value_list

    def _run_groupby_script(self, func, script, groupkeys, is_apply=False):
        groupby_size = (func == "size")
        groupby_having = (func == "")
        session = self._session
        index = groupkeys if self._as_index or groupby_size or groupby_having else []
        if isinstance(func, list):
            column_index = ([(col, func_name) for func_name in func]
                            for col in self._data_columns if col not in self._groupkeys)
            column_index = list(itertools.chain(*column_index))
            return get_orca_obj_from_script(session, script, index, column_index=column_index)
        if func == "ohlc":
            column_index = ([(col, "open"), (col, "high"), (col, "low"), (col, "close")] for col in self._data_columns)
            column_index = list(itertools.chain(*column_index))
            return get_orca_obj_from_script(session, script, index, column_index=column_index)
        data = get_orca_obj_from_script(session, script, index)
        if groupby_size:
            s = data["count"]
            s.rename(None, inplace=True)
            return s
        elif is_apply:
            s = data[data._data_columns[0]]
            s.rename(None, inplace=True)
            return s
        elif self._is_series_like:
            s = data[data._data_columns[0]]
            s.rename(self._name, inplace=True)
            return s
        else:
            return data

    def _get_data_select_list(self):
        internal = self._internal
        if isinstance(internal, (ArithExpression, BooleanExpression, MergeExpression)):
            return internal._get_data_select_list()
        else:
            return self._data_columns

    @abc.abstractmethod
    def _groupby_op(self, func, numeric_only):
        select_list, _ = \
            self._generate_groupby_select_list_and_value_list(func, self._groupkeys, numeric_only)
        if len(select_list) == 0:    # TODO: handle
            raise NotImplementedError()
        orderby_list = self._orderby_list if self._sort else None
        if isinstance(self._internal, MergeExpression):
            var_name = self._internal._from_clause
        else:
            var_name = self._var_name
        script = sql_select(select_list, var_name, self._where_expr,
                            groupby_list=self._groupby_list, orderby_list=orderby_list,
                            asc=self._ascending)
        return self._run_groupby_script(func, script, self._result_index_map)

    @abc.abstractmethod
    def _contextby_op(self, func, numeric_only):    # TODO: context by order
        select_list, value_list = \
            self._generate_groupby_select_list_and_value_list(func, self._groupkeys, numeric_only)
        klass = SeriesContextByExpression if self._is_series_like else DataFrameContextByExpression
        return klass(self._session, self._internal, func, self._where_expr, self._name,
                     select_list, value_list, self._groupby_list)


class ContextByExpression(_InternalAccessor):
    """
    Expression related to DolphinDB context by expressions.
    """

    def __init__(self, session, internal, func, where_expr, name,
                 select_list, value_list, groupby_list):
        self._session = session
        self._internal = internal
        self._func = func
        self._where_expr = where_expr
        self._name = name
        self._select_list = select_list
        self._value_list = value_list
        self._groupby_list = groupby_list
        self._as_index = True

    def compute(self):
        select_list = self._select_list
        if len(select_list) == 0:
            raise NotImplementedError()
        select_list = itertools.chain(self._index_columns, select_list)
        script = sql_select(select_list, self._var_name, self._where_expr,
                            groupby_list=self._groupby_list, is_groupby=False, hint=128)
        return GroupByOpsMixin._run_groupby_script(self, self._func, script, self._index_map)

    def to_pandas(self):
        return self.compute().to_pandas()

    def _get_data_select_list(self):
        return self._value_list

    def _get_contextby_list(self):
        return self._groupby_list


class DataFrameContextByExpression(DataFrameLike, ContextByExpression):

    pass


class SeriesContextByExpression(SeriesLike, ContextByExpression):

    pass



class GroupBy(_InternalAccessor, GroupByOpsMixin, metaclass=abc.ABCMeta):

    def __init__(self, session, internal, index, by, level, as_index, sort, ascending, where_expr, name,
                 groupkeys=None, groupby_list=None, orderby_list=None, result_index_map=None,
                 contextby_result_index_map=None):
        self._session = session
        self._internal = internal
        self._index = index
        self._as_index = as_index
        self._sort = sort
        self._ascending = ascending
        self._where_expr = where_expr
        self._name = name
        
        if (groupkeys is not None and groupby_list is not None
                and orderby_list is not None and result_index_map is not None
                and contextby_result_index_map is not None):
            self._groupkeys = groupkeys
            self._groupby_list = groupby_list
            self._orderby_list = orderby_list
            self._result_index_map = result_index_map
            self._contextby_result_index_map = contextby_result_index_map
            return

        index_names = []
        groupkeys = []
        if by is None and level is None:
            raise TypeError("You have to supply one of 'by' and 'level'")
        if level is not None:
            groupkeys, _, index_names, _ = _infer_level(level, self._index_map)
        else:
            for column in by:
                if isinstance(column, str):
                    groupkeys.append(column)
                    index_names.append(column)
                elif isinstance(column, Series):
                    if column._var_name != self._var_name:
                        raise ValueError("Unable to groupby with an external Series")
                    groupkeys.append(column._data_columns[0])
                    index_names.append(column._name)
                elif isinstance(column, Index):
                    if column._var_name != self._var_name:
                        raise ValueError("Unable to groupby with an external Index")
                    groupkeys += column._index_columns
                    index_names += column._index_columns
                elif isinstance(column, (ArithExpression, BooleanExpression)):
                    if not column._is_series_like:
                        raise ValueError("Grouper is not 1-dimensional")
                    if column._var_name != self._var_name:
                        raise ValueError("Unable to groupby with an external Index")
                    groupkeys.append(column._get_data_select_list()[0])
                    index_names.append(column._name)
                else:
                    raise ValueError("Each element in by must be a label")
        self._groupkeys = groupkeys

        self._groupby_list, self._orderby_list, \
        self._result_index_map, self._contextby_result_index_map = \
            GroupByOpsMixin._get_groupby_list_orderby_list_and_index_map(
                groupkeys, index_names, sort, resample=False)

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
            klass = SeriesGroupBy
            name = key
        elif isinstance(key, Iterable):
            klass = DataFrameGroupBy
            name = self._name
        else:
            raise KeyError(key)
        new_odf = self._internal[key]
        return klass(self._session, new_odf, self._index, None, None,
                     self._as_index, self._sort, self._ascending, self._where_expr, name,
                     self._groupkeys, self._groupby_list, self._orderby_list, self._result_index_map, self._contextby_result_index_map)

    def _groupby_op(self, *args, **kwargs):
        return GroupByOpsMixin._groupby_op(self, *args, **kwargs)
    
    def _contextby_op(self, *args, **kwargs):
        return GroupByOpsMixin._contextby_op(self, *args, **kwargs)
    
    def resample(self, rule, how=None, axis=0, fill_method=None, closed=None,
                 label=None, convention='start', kind=None, loffset=None,
                 limit=None, base=0, on=None, level=None, lazy=False, **kwargs):
        from .resample import SeriesResampler, DataFrameResampler
        klass = SeriesResampler if self._is_series_like else DataFrameResampler
        StatOpsMixin._validate_resample_arguments(how=how, axis=axis, fill_method=fill_method, closed=closed,
                                                  label=label, convention=convention, kind=kind, loffset=loffset,
                                                  limit=limit, base=base, on=on, level=level)
        return klass(self._session, self._internal, self._index, rule, on=on, level=level,
                     where_expr=self._where_expr, name=self._name, groupkeys=self._groupkeys, sort=self._sort)

    def filter(self, func, dropna=True, *args, **kwargs):
        if not dropna:
            raise NotImplementedError()
        if not isinstance(func, str):
            raise ValueError("Orca does not support callable func; func must be a string representing a HAVING condition")
        index_columns = self._index_columns
        select_list = index_columns + self._get_data_select_list()
        script = sql_select(select_list, self._var_name, self._where_expr,
                            groupby_list=self._groupby_list, is_groupby=False,
                            having_list=[func])
        return self._run_groupby_script("", script, self._index_map)


class DataFrameGroupBy(DataFrameLike, GroupBy):

    pass


class SeriesGroupBy(SeriesLike, GroupBy):

    pass


class HavingGroupBy(_InternalAccessor, GroupByOpsMixin, metaclass=abc.ABCMeta):

    @property
    @abc.abstractmethod
    def _is_series_like(self):
        pass

    @property
    @abc.abstractmethod
    def _is_dataframe_like(self):
        pass


class DataFrameHavingGroupBy(DataFrameLike, HavingGroupBy):

    pass


class SeriesHavingGroupBy(DataFrameLike, HavingGroupBy):

    pass
