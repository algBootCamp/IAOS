import abc
import itertools
from typing import Iterable

from pandas.tseries.frequencies import to_offset

from .indexes import DatetimeIndex
from .internal import _InternalAccessor
from .operator import DataFrameLike, EwmOpsMixin, SeriesLike, StatOpsMixin
from .utils import (
    _scale_nanos, check_key_existence, dolphindb_numeric_types,
    dolphindb_temporal_types, get_orca_obj_from_script, sql_select,
    to_dolphindb_literal)


def _orca_window_op(func, numeric_only, use_moving_template=False):
    def wfunc(self):
        return self._window_op(func, numeric_only, use_moving_template)
    return wfunc

def _orca_window_covcorr(func, numeric_only=True, use_moving_template=True):
    def wfunc(self, other=None):
        return self._window_covcorr(func, other, numeric_only, use_moving_template)
    return wfunc

class WindowOpsMixin(metaclass=abc.ABCMeta):

    count = _orca_window_op("count", numeric_only=False)
    sum = _orca_window_op("sum", numeric_only=True)
    mean = _orca_window_op("avg", numeric_only=True)
    median = _orca_window_op("med", numeric_only=True)
    var = _orca_window_op("var", numeric_only=True)
    std = _orca_window_op("std", numeric_only=True)
    min = _orca_window_op("min", numeric_only=True)
    max = _orca_window_op("max", numeric_only=True)
    skew = _orca_window_op("skew", numeric_only=True, use_moving_template=True)
    kurtosis = _orca_window_op("kurtosis", numeric_only=True, use_moving_template=True)
    kurt = kurtosis
    argmax = _orca_window_op("imax", numeric_only=False)
    argmin = _orca_window_op("imin", numeric_only=False)

    corr = _orca_window_covcorr("corr")
    cov = _orca_window_covcorr("cov")

    @abc.abstractmethod
    def _window_op(self, func, numeric_only, use_moving_template):
        pass


class Rolling(_InternalAccessor, WindowOpsMixin, metaclass=abc.ABCMeta):

    _ROLLING_COLUMN = "ORCA_ROLLING_COLUMN"

    def __init__(self, session, internal, index, window, min_periods, on, where_expr, name, rolling_on_temporal=None):
        self._session = session
        self._internal = internal
        self._index = index
        self._on = on
        self._where_expr = where_expr
        self._name = name
        if min_periods is None or isinstance(min_periods, int):
            self._min_periods = min_periods
        else:
            raise ValueError("min_periods must be an integer or None")

        if rolling_on_temporal is not None:
            self._window = window
            self._rolling_on_temporal = rolling_on_temporal
            return

        if on is not None:
            check_key_existence(on, self._data_columns)

        if isinstance(window, int):
            self._window = window
            self._rolling_on_temporal = False
            if min_periods is None:
                self._min_periods = window
        else:
            self._window = self._match_offset(window)
            if on is not None:
                if self._ddb_dtypes[on] not in dolphindb_temporal_types:
                    raise ValueError("window must be an integer")
            elif not isinstance(self._index, DatetimeIndex):
                raise ValueError("window must be an integer")
            if self._min_periods is not None and self._min_periods > 1:
                raise ValueError("if window is offset, min_periods more than 1 is not supported yet")
            self._rolling_on_temporal = True

    @abc.abstractproperty
    def _is_series_like(self):
        pass

    @abc.abstractproperty
    def _is_dataframe_like(self):
        pass

    @property
    def _index_column(self):
        return self._index_columns[0]

    def __getitem__(self, key):
        if isinstance(key, str):
            klass = SeriesRolling
            name = key
        elif isinstance(key, Iterable):
            klass = DataFrameRolling
            name = self._name
        else:
            raise KeyError(key)
        new_odf = self._internal[key]
        return klass(self._session, new_odf, self._index, self._window, self._min_periods,
                     self._on, self._where_expr, name, self._rolling_on_temporal)

    def _match_offset(self, rule):
        offset = to_offset(rule)
        offset_fixed = offset - offset.base
        on = self._on
        if on is None:
            col = self._index_column
        else:
            col = on
        ddb_dtype = self._ddb_dtypes[col]
        nanos = _scale_nanos(offset_fixed.nanos, ddb_dtype)
        return nanos

    def _cols_with_and_without_on(self, numeric_only):
        on, ddb_dtypes, data_columns = self._on, self._ddb_dtypes, self._data_columns
        cols_with_on = [col for col in data_columns
                        if (not numeric_only
                            or ddb_dtypes[col] in dolphindb_numeric_types
                            or col == on)]
        cols = [col for col in cols_with_on if col != on]
        return cols, cols_with_on

    def _window_op(self, func, numeric_only, use_moving_template):
        if self._rolling_on_temporal:
            data = self._window_op_on_temporal(func, numeric_only)
        else:
            data = self._window_op_on_non_temporal(func, numeric_only, use_moving_template)
        if self._is_series_like:
            column = data._data_columns[0]
            return data[column]
        else:
            return data

    def _window_covcorr(self, func, other=None, numeric_only=True, use_moving_template=True):
        if self._rolling_on_temporal:
            on = self._on
            cols, cols_with_on = self._cols_with_and_without_on(numeric_only)
            agg_list = [f"{func}({cols[i]}, {other._var_name}.{other._data_columns[i]}) as {self._ROLLING_COLUMN}_{cols[i]}" for i in range(0, cols)]
            agg_script = "<[" + ",".join(agg_list) + "]>"
            if self._where_expr is not None:
                raise NotImplementedError()
            var_name = self._var_name
            window = self._window
            on_literal = to_dolphindb_literal(self._on or self._index_column)
            from_clause = f"wj({var_name}, {var_name}, -{window}:0, {agg_script}, {on_literal})"
            select_list = (f"{self._ROLLING_COLUMN}_{col} as {col}"
                           if col != on else col
                           for col in cols_with_on)
            select_list = itertools.chain(self._index_columns, select_list)
            script = sql_select(select_list, from_clause)
            data = get_orca_obj_from_script(
                self._session, script, self._index_map, name=self._name)

        else:
            #if self._is_series_like:
            #    window = self._window
            #    if use_moving_template:
            #        func = f"moving{{{func},,{window}}}"
            #    else:
            #        func = f"m{func}{{,{window}}}"
            #    data = StatOpsMixin._unary_op(self, func, numeric_only)
            if self._is_series_like and other is None:
                raise TypeError(f"{func}() missing 1 required positional argument: 'other'")
            if other is None:
                on = self._on
                _, cols_with_on = self._cols_with_and_without_on(numeric_only)
                if self._min_periods is not None:
                    gen_moving_col = "moving({func}, {col}, {window}, {min_periods}) as {col}"
                else:
                    gen_moving_col = "m{func}({col}, {window}, {min_periods}) as {col}"
                select_list = (gen_moving_col.format(func=func, col=col, window=self._window, min_periods=self._min_periods)
                               if col != on else col
                               for col in cols_with_on)
                select_list = itertools.chain(self._index_columns, select_list)
                script = sql_select(select_list, self._var_name, self._where_expr)
                data = get_orca_obj_from_script(
                    self._session, script, self._index_map, name=self._name)
            else:
                on = self._on
                _, cols_with_on = self._cols_with_and_without_on(numeric_only)
                if use_moving_template:
                    gen_moving_col = "moving({func}, {colx}, {window}, {min_periods}) as {col}"
                else:
                    gen_moving_col = "m{func}({colx}, {window}, {min_periods}) as {col}"

                select_list = (gen_moving_col.format(func=func, colx=f"[{cols_with_on[i]}, {other._var_name}.{other._data_columns[i]}]", window=self._window, min_periods=self._min_periods, col = cols_with_on[i])
                               if cols_with_on[i] != on else cols_with_on[i]
                               for i in range(0, len(cols_with_on)))

                select_list = itertools.chain(self._index_columns, select_list)
                script = sql_select(select_list, self._var_name, self._where_expr)
                data = get_orca_obj_from_script(
                    self._session, script, self._index_map, name=self._name)

        if self._is_series_like:
            column = data._data_columns[0]
            return data[column]
        else:
            return data

    def _get_data_select_list(self):
        return self._data_columns

    def _window_op_on_non_temporal(self, func, numeric_only, use_moving_template):
        if func == "count":
            self._min_periods = None
        if self._is_series_like:
            window = self._window
            min_periods = self._min_periods
            if use_moving_template:
                if min_periods is not None:
                    func = f"moving{{{func},,{window}, {min_periods}}}"
                else:
                    func = f"moving{{{func},,{window}}}"
            else:
                if min_periods is not None:
                    func = f"m{func}{{,{window}, {min_periods}}}"
                else:
                    func = f"m{func}{{,{window}}}"
            return StatOpsMixin._unary_op(self, func, numeric_only)
        else:
            on = self._on
            _, cols_with_on = self._cols_with_and_without_on(numeric_only)
            if use_moving_template:
                if self._min_periods is not None:
                    gen_moving_col = "moving({func}, {col}, {window}, {min_periods}) as {col}"
                else:
                    gen_moving_col = "moving({func}, {col}, {window}) as {col}"
            else:
                if self._min_periods is not None:
                    gen_moving_col = "m{func}({col}, {window}, {min_periods}) as {col}"
                else:
                    gen_moving_col = "m{func}({col}, {window}) as {col}"
            select_list = (gen_moving_col.format(func=func, col=col, window=self._window, min_periods=self._min_periods)
                               if col != on else col
                               for col in cols_with_on)
            select_list = itertools.chain(self._index_columns, select_list)
            script = sql_select(select_list, self._var_name, self._where_expr)
            return get_orca_obj_from_script(
                self._session, script, self._index_map, name=self._name)

    def _window_op_on_temporal(self, func, numeric_only):
        on = self._on
        cols, cols_with_on = self._cols_with_and_without_on(numeric_only)
        agg_list = [f"{func}({col}) as {self._ROLLING_COLUMN}_{col}" for col in cols]
        agg_script = "<[" + ",".join(agg_list) + "]>"
        if self._where_expr is not None:
            raise NotImplementedError()
        var_name = self._var_name
        window = self._window
        on_literal = to_dolphindb_literal(self._on or self._index_column)
        from_clause = f"wj({var_name}, {var_name}, -{window}:0, {agg_script}, {on_literal})"
        select_list = (f"{self._ROLLING_COLUMN}_{col} as {col}"
                       if col != on else col
                       for col in cols_with_on)
        select_list = itertools.chain(self._index_columns, select_list)
        script = sql_select(select_list, from_clause)
        return get_orca_obj_from_script(
            self._session, script, self._index_map, name=self._name)

class DataFrameRolling(DataFrameLike, Rolling):

    pass


class SeriesRolling(SeriesLike, Rolling):

    pass


class Ewm(_InternalAccessor, EwmOpsMixin, metaclass=abc.ABCMeta):

    def __init__(self, session, internal, index, com, span, halflife, alpha, min_periods, adjust, ignore_na, where_expr):
        self._session = session
        self._internal = internal
        self._index = index

        if com is None:
            com = ""
        elif com < 0:
            raise ValueError("com must greater than 0")
        if span is None:
            span = ""
        elif span < 1:
            raise ValueError("span must greater than 1")
        if halflife is None:
            halflife = ""
        elif halflife <= 0:
            raise ValueError("halflife must greater than 0")
        if alpha is None:
            alpha = ""
        elif alpha < 0 or alpha > 1:
            raise ValueError("alpha must between 0 and 1")
        if adjust:
            adjust = "true"
        else:
            adjust = "false"
        if ignore_na:
            ignore_na = "true"
        else:
            ignore_na = "false"

        self._com = com
        self._span = span
        self._halflife = halflife
        self._alpha = alpha
        self._min_periods = min_periods
        self._adjust = adjust
        self._ignore_na = ignore_na

        self._where_expr = where_expr


    def __getitem__(self, key):
        if isinstance(key, str):
            klass = SeriesEwm
        elif isinstance(key, Iterable):
            klass = DataFrameEwm
        else:
            raise KeyError(key)
        new_odf = self._internal[key]
        return klass(self._session, new_odf, self._index, self._com, self._span, self._halflife, self._alpha, self._min_periods, self._adjust, self._ignore_na)

    def _cols_with_and_without_on(self, numeric_only):
        on, ddb_dtypes, data_columns = None, self._ddb_dtypes, self._data_columns
        cols_with_on = [col for col in data_columns
                        if (not numeric_only
                            or ddb_dtypes[col] in dolphindb_numeric_types
                            or col == on)]
        cols = [col for col in cols_with_on if col != on]
        return cols, cols_with_on

    def _ewm_op(self, func, bias=False):
        if bias:
            bias = "true"
        else:
            bias = "false"
        _, cols_with_on = self._cols_with_and_without_on(True)
        if func in ["ewmStd", "ewmVar"]:
            gen_moving_col = "{func}({col}, {com}, {span}, {halflife}, {alpha}, {min_periods}, {adjust}, {ignore_na}, {bias}) as {col}"
            select_list = (gen_moving_col.format(func=func, col=col, com=self._com, span=self._span,halflife=self._halflife, alpha=self._alpha, min_periods=self._min_periods, adjust=self._adjust, ignore_na=self._ignore_na, bias=bias) for col in cols_with_on)
        else:
            gen_moving_col = "{func}({col}, {com}, {span}, {halflife}, {alpha}, {min_periods}, {adjust}, {ignore_na}) as {col}"
            select_list = (gen_moving_col.format(func=func, col=col, com=self._com, span=self._span,halflife=self._halflife, alpha=self._alpha, min_periods=self._min_periods, adjust=self._adjust, ignore_na=self._ignore_na) for col in cols_with_on)

        select_list = itertools.chain(self._index_columns, select_list)

        script = sql_select(select_list, self._var_name, self._where_expr)

        data = get_orca_obj_from_script(
            self._session, script, self._index_map, name=None)

        if self._is_series_like:
            column = data._data_columns[0]
            return data[column]
        else:
            return data

    def _ewm_covcorr(self, func, other=None, bias=False, method='pearson', min_periods=1):
        if func=="ewmCorr" and method != "pearson":
            raise ValueError(f"method must be 'pearson', '{method}' was supplied")
        from .frame import DataFrame
        #if min_periods != 1:
        #    raise NotImplementedError()
        #if self._is_series_like and other is None:
        #    raise TypeError(f"{func}() missing 1 required positional argument: 'other'")

        if bias:
            bias = "true"
        else:
            bias = "false"
        session = self._session

        _, cols_with_on = self._cols_with_and_without_on(True)
        if other is None:
            gen_moving_col = "{func}({col}, {com}, {span}, {halflife}, {alpha}, {min_periods}, {adjust}, {ignore_na},,{bias}) as {col}"
            select_list = (gen_moving_col.format(func=func, col=col, com=self._com, span=self._span,halflife=self._halflife, alpha=self._alpha, min_periods=self._min_periods, adjust=self._adjust, ignore_na=self._ignore_na, bias=bias) for col in cols_with_on)
        else:
            gen_moving_col = "{func}({col}, {com}, {span}, {halflife}, {alpha}, {min_periods}, {adjust}, {ignore_na}, {other},{bias}) as {col}"
            select_list = (gen_moving_col.format(func=func, col=cols_with_on[i], com=self._com, span=self._span, halflife=self._halflife, alpha=self._alpha, min_periods=self._min_periods, adjust=self._adjust, ignore_na=self._ignore_na, other=f"{other._var_name}.{other._data_columns[i]}", bias=bias) for i in range(0, len(cols_with_on)))

        select_list = itertools.chain(self._index_columns, select_list)

        script = sql_select(select_list, self._var_name, self._where_expr)

        data = get_orca_obj_from_script(
            self._session, script, self._index_map, name=None)

        if self._is_series_like:
            column = data._data_columns[0]
            return data[column]
        else:
            return data



    @property
    def _index_column(self):
        return self._index_columns[0]

    @abc.abstractproperty
    def _is_series_like(self):
        pass

    @abc.abstractproperty
    def _is_dataframe_like(self):
        pass



class DataFrameEwm(DataFrameLike, Ewm):

    pass


class SeriesEwm(SeriesLike, Ewm):

    pass


class WindowJoiner(object):

    def __init__(self, session, method, window, left_odf, right_odf,
                 left_join_columns, right_join_columns, where_expr):
        self._session = session
        self._method = method
        self._window = window
        self._left_odf = left_odf
        self._right_odf = right_odf
        self._left_join_columns = left_join_columns
        self._right_join_columns = right_join_columns
        self._where_expr = where_expr

    def aggregate(self, func):
        if not isinstance(func, dict):
            raise TypeError("func must be dictionary")
        agg_functions = []
        for key, value in func.items():
            if not isinstance(key, str):
                raise TypeError("Every key in func must be a string")
            if not isinstance(value, str):
                raise TypeError("Every value in func must be a string")
            agg_functions.append(f"{value} as {key}")
        session = self._session
        method = self._method
        window = self._window
        left_var_name = self._left_odf._var_name
        right_var_name = self._right_odf._var_name
        left_join_literal = to_dolphindb_literal(self._left_join_columns)
        right_join_literal = to_dolphindb_literal(self._right_join_columns)
        agg_functions_script = ",".join(agg_functions)
        script = f"{method}({left_var_name}, {right_var_name}, {window}, " \
                 f"<[{agg_functions_script}]>, " \
                 f"{left_join_literal}, {right_join_literal})"
        return get_orca_obj_from_script(session, script, index_map=None)

    agg = aggregate
