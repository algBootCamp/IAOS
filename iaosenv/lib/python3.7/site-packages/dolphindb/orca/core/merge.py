import itertools

from .base import _Frame
from .common import _raise_must_compute_error
from .datetimes import Timestamp
from .internal import _ConstantSP
# from .groupby import GroupByOpsMixin, _orca_contextby_op, _orca_groupby_op
from .operator import (ArithExpression, ArithOpsMixin, BooleanExpression,
                       IOOpsMixin, LogicalOpsMixin, StatOpsMixin,
                       _get_expr_with_binary_op, _orca_binary_op,
                       _orca_extended_binary_op,
                       _orca_extended_reversed_binary_op,
                       _orca_reversed_binary_op, _orca_unary_agg_op,
                       _orca_unary_op)
from .utils import (_merge_where_expr, _new_orca_identifier,
                    _try_convert_iterable_to_list, check_key_existence,
                    get_orca_obj_from_script, is_dolphindb_integral,
                    sql_select, to_dolphindb_literal)
from .window import WindowJoiner


def _generate_joiner(left_var_name, right_var_name,
                     left_join_columns, right_join_columns, 
                     how="outer", sort=False, use_right_index=False):
        """
        Returns the index_list and from_clause used in binary operations on
        Frames with different indices.
        """
        if len(left_join_columns) != len(right_join_columns):
            raise ValueError("cannot join with no overlapping index names")
        if sort:
            methods = {"left_semi": "slsj", "left": "slj", "right": "slj",
                       "outer": "sfj", "inner": "sej"}
        else:
            methods = {"left_semi": "lsj", "left": "lj", "right": "lj",
                       "outer": "fj", "inner": "ej", "asof": "aj"}
        method = methods.get(how, None)
        if method is None:
            raise ValueError(f"Unrecognize join method {how}")

        left_join_literal = to_dolphindb_literal(left_join_columns)
        right_join_literal = to_dolphindb_literal(right_join_columns)
        if how == "right":
            index_list = (f"{right_var_name}.{col} as {col}" for col in right_join_columns)
        elif how in ("left", "left_semi"):
            index_list = (f"{left_var_name}.{col} as {col}" for col in left_join_columns)
        else:
            index_list = (
                f"iif(isValid({left_var_name}.{left_col}), "
                f"{left_var_name}.{left_col}, "
                f"{right_var_name}.{right_col}) "
                f"as {right_col if use_right_index else left_col}"
                for left_col, right_col
                in zip(left_join_columns, right_join_columns)
            )
        if how == "right":
            from_clause = f"{method}({right_var_name}, {left_var_name}, " \
                          f"{right_join_literal}, {left_join_literal})"
        else:
            from_clause = f"{method}({left_var_name}, {right_var_name}, " \
                          f"{left_join_literal}, {right_join_literal})"
        return index_list, from_clause


def _validate_on(on, left_on, right_on):
    if on is not None:
        if left_on is not None or right_on is not None:
            # TODO: pandas.errors.MergeError
            raise ValueError('Can only pass argument "on" OR "left_on" and "right_on", not a combination of both.')
        left_on = right_on = _try_convert_iterable_to_list(on)
    else:
        left_on = _try_convert_iterable_to_list(left_on)
        right_on = _try_convert_iterable_to_list(right_on)
    return left_on, right_on


def _validate_left_right(left, right):
    if (isinstance(left, (ArithExpression, BooleanExpression))
            or isinstance(right, (ArithExpression, BooleanExpression))):
        _raise_must_compute_error("Can only merge Series or DataFrame objects")
    if not isinstance(left, _Frame) or not left._is_dataframe_like:
        raise TypeError(f"Can only merge Series or DataFrame objects, a {type(left)} was passed")
    if not isinstance(right, _Frame):
        raise TypeError('other must be a DataFrame or a Series')
    elif right._is_series_like and right.name is None:
        raise TypeError('Other Series must have a name')


def _validate_suffixes(suffixes):
    lsuf, rsuf = suffixes
    if not isinstance(lsuf, str) or not isinstance(rsuf, str):
        raise TypeError("Both lsuffix and rsuffix must be strings")
    return lsuf, rsuf


def _get_left_right_data_join_columns(left, right, on, left_on, right_on,
                                      left_index, right_index):
    """
    Return (left_data_columns, left_join_columns,
            right_data_columns, right_join_columns, force_index)
    """
    left_data_columns, right_data_columns = left._data_columns, right._data_columns
    overlap_columns = set(left_data_columns) & set(right_data_columns)
    left_on, right_on = _validate_on(on, left_on, right_on)
    force_index = False
    if left_index and not right_index:
        force_index = any(on in overlap_columns for on in right_on)
    elif not left_index and right_index:
        force_index = any(on in overlap_columns for on in left_on)

    if left_index:
        left_join_columns = left._index_columns
    elif force_index:
        try:
            left_join_columns, _ = check_key_existence(left_on, left_data_columns)
        except KeyError:
            left_join_columns, _ = check_key_existence(left_on, left_data_columns + left._index_columns)
    else:
        try:
            left_join_columns, left_data_columns = check_key_existence(left_on, left_data_columns)
        except KeyError:
            left_join_columns, left_data_columns = check_key_existence(left_on, left_data_columns + left._index_columns)

    if right_index:
        right_join_columns = right._index_columns
    elif force_index:
        try:
            right_join_columns, _ = check_key_existence(right_on, right_data_columns)
        except KeyError:
            right_join_columns, _ = check_key_existence(right_on, right_data_columns + right._index_columns)
    else:
        try:
            right_join_columns, right_data_columns = check_key_existence(right_on, right_data_columns)
        except KeyError:
            right_join_columns, right_data_columns = check_key_existence(right_on, right_data_columns + right._index_columns)
    if len(left_join_columns) != len(right_join_columns):
        raise ValueError("len(right_on) must equal len(left_on)")
    return left_data_columns, left_join_columns, right_data_columns, right_join_columns, force_index


def _get_join_list(overlap_columns, tb_name, suf, data_columns, ddb_dtypes):
    def overlap_checked_data_column(col):
        return col + suf if col in overlap_columns else col
    new_data_columns = [overlap_checked_data_column(col) for col in data_columns]
    select_list = [f"{tb_name}.{col}" for col in data_columns]
    new_ddb_dtypes = ddb_dtypes[data_columns]
    return select_list, new_data_columns, new_ddb_dtypes.set_axis(new_data_columns, inplace=False)


def _add_force_index(index_list, left_columns, left_data_columns, left_ddb_dtypes,
                     right_join_columns, right_data_columns, right_ddb_dtypes):
    join_columns, join_data_columns = [], []
    for col in right_data_columns:
        try:
            idx = right_join_columns.index(col)
            column_alias_script = index_list[idx]
            column_alias_script = column_alias_script[:column_alias_script.index(" as ")]
            join_columns.append(column_alias_script)
            join_data_columns.append(col)
        except:
            pass
    left_columns = join_columns + left_columns
    left_data_columns = join_data_columns + left_data_columns
    left_ddb_dtypes = right_ddb_dtypes[join_data_columns].append(left_ddb_dtypes)
    return left_columns, left_data_columns, left_ddb_dtypes


def merge(left, right, how='inner', on=None, left_on=None, right_on=None,
          left_index=False, right_index=False, sort=False, suffixes=('_x', '_y'),
          copy=True, indicator=False, validate=None, lazy=False):
    # TODO: return internal expression
    _validate_left_right(left, right)
    if sort:    # TDOO: sort
        if how not in ('inner'):
            raise NotImplementedError()
    if how == "asof":
        raise ValueError(f"Unrecognize join method {how}")
    lsuf, rsuf = _validate_suffixes(suffixes)
    left_var_name, right_var_name = left._var_name, right._var_name
    left_data_columns, left_join_columns, right_data_columns, right_join_columns, force_index = \
        _get_left_right_data_join_columns(
            left, right, on, left_on, right_on,
            left_index, right_index)
    overlap_columns = set(left_data_columns) & set(right_data_columns)
    if overlap_columns and not lsuf and not rsuf:
        raise ValueError(f"columns overlap but no suffix specified: "
                         f"{list(overlap_columns)}")

    index_list, from_clause = _generate_joiner(
        left._var_name, right._var_name,
        left_join_columns, right_join_columns, how=how, sort=sort)
    index_list = list(index_list)
    if left_index and not right_index:
        index_columns = [f"{right_var_name}.{col} as {col}" for col in right._index_columns]
        left_columns, left_data_columns, left_ddb_dtypes = \
            _get_join_list(overlap_columns, left_var_name, lsuf,
                           left._data_columns, left._ddb_dtypes)
        if force_index:
            left_columns, left_data_columns, left_ddb_dtypes = \
                _add_force_index(index_list, left_columns, left_data_columns, left_ddb_dtypes,
                                 right_join_columns, right_data_columns, right._ddb_dtypes)
        right_columns, right_data_columns, right_ddb_dtypes = \
            _get_join_list(overlap_columns, right_var_name, rsuf,
                           right._data_columns, right._ddb_dtypes)
        index_map = right._index_map
    elif right_index and not left_index:
        index_columns = [f"{left_var_name}.{col} as {col}" for col in left._index_columns]
        left_columns, left_data_columns, left_ddb_dtypes = \
            _get_join_list(overlap_columns, left_var_name, lsuf,
                           left._data_columns, left._ddb_dtypes)
        if force_index:
            left_columns, left_data_columns, left_ddb_dtypes = \
                _add_force_index(index_list, left_columns, left_data_columns,
                                 left_ddb_dtypes, left_join_columns, left_data_columns, left._ddb_dtypes)
        right_columns, right_data_columns, right_ddb_dtypes = \
            _get_join_list(overlap_columns, right_var_name, rsuf,
                           right._data_columns, right._ddb_dtypes)
        index_map = left._index_map
    elif not left_index and not right_index:
        index_columns = []
        left_columns, left_data_columns, left_ddb_dtypes = \
            _get_join_list(overlap_columns, left_var_name, lsuf,
                           left._data_columns, left._ddb_dtypes)
        right_columns, right_data_columns, right_ddb_dtypes = \
            _get_join_list(overlap_columns, right_var_name, rsuf,
                           right_data_columns, right._ddb_dtypes)
        index_map = None
    else:
        index_columns = index_list
        left_columns, left_data_columns, left_ddb_dtypes = \
            _get_join_list(overlap_columns, left_var_name, lsuf,
                           left_data_columns, left._ddb_dtypes)
        right_columns, right_data_columns, right_ddb_dtypes = \
            _get_join_list(overlap_columns, right_var_name, rsuf,
                           right_data_columns, right._ddb_dtypes)
        index_map = left._index_map

    session = left._session
    where_expr = _merge_where_expr(left._where_expr, right._where_expr)

    if not lazy:
        left_script = (f"{column} as {data_column}"
                       for column, data_column in zip(left_columns, left_data_columns))
        rigth_script = (f"{column} as {data_column}"
                        for column, data_column in zip(right_columns, right_data_columns))
        select_list = itertools.chain(index_columns, left_script, rigth_script)
        script = sql_select(select_list, from_clause, where_expr)
        return get_orca_obj_from_script(session, script, index_map=index_map)
    else:
        return MergeExpression._raw_merge_expression(
            session, from_clause, left._var_name, right._var_name,
            index_columns, left_columns + right_columns, left_ddb_dtypes.append(right_ddb_dtypes),
            index_map, left_data_columns + right_data_columns, where_expr)


def merge_asof(left, right, on=None, left_on=None, right_on=None,
               left_index=False, right_index=False,
               by=None, left_by=None, right_by=None,
               suffixes=('_x', '_y'), tolerance=None,
               allow_exact_matches=True, direction='backward', lazy=False):
    if tolerance is not None:
        raise NotImplementedError()
    if not allow_exact_matches:
        raise NotImplementedError()
    if direction != "backward":
        raise NotImplementedError()

    _validate_left_right(left, right)
    left_on, right_on = _validate_on(on, left_on, right_on)
    if by is not None:
        if left_by is not None or right_by is not None:
            raise ValueError('Can only pass argument "by" OR "left_by" and "right_by", not a combination of both.')
        left_by = right_by = _try_convert_iterable_to_list(by)
    elif left_by is not None and right_by is None:
        raise ValueError("missing right_by")    # TODO: pandas.errors.MergeError
    elif left_by is None and right_by is not None:
        raise ValueError("missing left_by")    # TODO: pandas.errors.MergeError
    else:
        left_by = _try_convert_iterable_to_list(left_by)
        right_by = _try_convert_iterable_to_list(right_by)
        if len(left_by) != len(right_by):
            raise ValueError("left_by and right_by must be of same length")    # TODO: pandas.errors.MergeError
    lsuf, rsuf = _validate_suffixes(suffixes)

    # _get_left_right_data_join_columns
    left_var_name, right_var_name = left._var_name, right._var_name
    left_data_columns, right_data_columns = left._data_columns, right._data_columns
    left_on = left_by + left_on
    right_on = right_by + right_on
    if left_index:
        left_join_columns = left_by + left._index_columns
    else:
        try:
            left_join_columns, left_data_columns = check_key_existence(left_on, left_data_columns)
        except KeyError:
            left_join_columns, left_data_columns = check_key_existence(left_on, left_data_columns + left._index_columns)

    if right_index:
        right_join_columns = right_by + right._index_columns
    else:
        try:
            right_join_columns, right_data_columns = check_key_existence(right_on, right_data_columns)
        except KeyError:
            right_join_columns, right_data_columns = check_key_existence(right_on, right_data_columns + right._index_columns)

    overlap_columns = set(left_data_columns) & set(right_data_columns)
    if overlap_columns and not lsuf and not rsuf:
        raise ValueError(f"columns overlap but no suffix specified: "
                         f"{list(overlap_columns)}")

    index_list, from_clause = _generate_joiner(
        left._var_name, right._var_name,
        left_join_columns, right_join_columns, how="asof")
    # TODO: copy from merge
    # FIXME: bugs
    index_list = list(index_list)
    if left_index and not right_index:
        index_columns = [f"{right_var_name}.{col} as {col}" for col in right._index_columns]
        left_columns, left_data_columns, left_ddb_dtypes = \
            _get_join_list(overlap_columns, left_var_name, lsuf,
                           left._data_columns, left._ddb_dtypes)
        # if force_index:
        #     left_columns, left_data_columns, left_ddb_dtypes = \
        #         _add_force_index(index_list, left_columns, left_data_columns, left_ddb_dtypes,
        #                          right_join_columns, right_data_columns, right._ddb_dtypes)
        right_columns, right_data_columns, right_ddb_dtypes = \
            _get_join_list(overlap_columns, right_var_name, rsuf,
                           right._data_columns, right._ddb_dtypes)
        index_map = right._index_map
    elif right_index and not left_index:
        index_columns = [f"{left_var_name}.{col} as {col}" for col in left._index_columns]
        left_columns, left_data_columns, left_ddb_dtypes = \
            _get_join_list(overlap_columns, left_var_name, lsuf,
                           left._data_columns, left._ddb_dtypes)
        # if force_index:
        #     left_columns, left_data_columns, left_ddb_dtypes = \
        #         _add_force_index(index_list, left_columns, left_data_columns,
        #                          left_ddb_dtypes, left_join_columns, left_data_columns, left._ddb_dtypes)
        right_columns, right_data_columns, right_ddb_dtypes = \
            _get_join_list(overlap_columns, right_var_name, rsuf,
                           right._data_columns, right._ddb_dtypes)
        index_map = left._index_map
    elif not left_index and not right_index:
        index_columns = []
        left_columns, left_data_columns, left_ddb_dtypes = \
            _get_join_list(overlap_columns, left_var_name, lsuf,
                           left._data_columns, left._ddb_dtypes)
        right_columns, right_data_columns, right_ddb_dtypes = \
            _get_join_list(overlap_columns, right_var_name, rsuf,
                           right_data_columns, right._ddb_dtypes)
        index_map = None
    else:
        index_columns = index_list
        left_columns, left_data_columns, left_ddb_dtypes = \
            _get_join_list(overlap_columns, left_var_name, lsuf,
                           left_data_columns, left._ddb_dtypes)
        right_columns, right_data_columns, right_ddb_dtypes = \
            _get_join_list(overlap_columns, right_var_name, rsuf,
                           right_data_columns, right._ddb_dtypes)
        index_map = left._index_map

    session = left._session
    where_expr = _merge_where_expr(left._where_expr, right._where_expr)

    if not lazy:
        left_script = (f"{column} as {data_column}"
                       for column, data_column in zip(left_columns, left_data_columns))
        rigth_script = (f"{column} as {data_column}"
                        for column, data_column in zip(right_columns, right_data_columns))
        select_list = itertools.chain(index_columns, left_script, rigth_script)
        script = sql_select(select_list, from_clause, where_expr)
        return get_orca_obj_from_script(session, script, index_map=index_map)
    else:
        return MergeExpression._raw_merge_expression(
            session, from_clause, left._var_name, right._var_name,
            index_columns, left_columns + right_columns, left_ddb_dtypes.append(right_ddb_dtypes),
            index_map, left_data_columns + right_data_columns, where_expr)


def merge_window(left, right, window_lower, window_upper, prevailing=False, on=None,
                 left_on=None, right_on=None, left_index=False, right_index=False):
    _validate_left_right(left, right)
    if not is_dolphindb_integral(window_lower) or not is_dolphindb_integral(window_upper):
        raise TypeError("Both window_lower and window_upper must be integers")
    _, left_join_columns, _, right_join_columns, _ = \
        _get_left_right_data_join_columns(
            left, right, on, left_on, right_on, left_index, right_index)

    window = f"{window_lower}:{window_upper}"
    method = "pwj" if prevailing else "wj"
    where_expr = _merge_where_expr(left._where_expr, right._where_expr)
    return WindowJoiner(left._session, method, window, left._internal, right._internal,
                        left_join_columns, right_join_columns, where_expr)


class MergeExpression(ArithOpsMixin, LogicalOpsMixin, StatOpsMixin, IOOpsMixin):

    def __init__(self, left, right, func, axis):
        self._left = left
        self._right = right
        self._func = func

        core_obj, other_obj = (right, left) if isinstance(left, _ConstantSP) else (left, right)
        self._where_expr = core_obj._where_expr
        self._left_var_name = core_obj._left_var_name
        self._right_var_name = core_obj._right_var_name
        self._data_columns = core_obj._data_columns
        self._session = core_obj._session
        self._ddb_dtypes = core_obj._ddb_dtypes
        self._index = core_obj._index
        self._name = core_obj._name
        if axis == 1:
            raise NotImplementedError()    # TODO: support axis == 1
        # prepare the select list
        if isinstance(other_obj, (_ConstantSP, Timestamp)):
            self._is_series_like = core_obj._is_series_like
            self._is_dataframe_like = core_obj._is_dataframe_like
            if isinstance(left, _ConstantSP) and axis == 0:
                self._data_select_list = [
                    f"{func}({left._var_name}, {script})" for script in right._get_data_select_list()]
            elif isinstance(left, Timestamp):
                raise NotImplementedError()    # TODO: support Timestamp
            elif isinstance(right, _ConstantSP) and axis == 0:
                self._data_select_list = [f"{func}({script}, {right._var_name})" for script in left._get_data_select_list()]
            elif isinstance(right, Timestamp):
                raise NotImplementedError()    # TODO: support Timestamp
        elif right is None:
            self._is_series_like = left._is_series_like
            self._is_dataframe_like = left._is_dataframe_like

            if isinstance(func, dict) or func.startswith("isDuplicated"):
                raise NotImplementedError()
            else:
                self._data_select_list = [f"{func}({script})" for script in left._data_select_list]
        else:
            self._is_series_like = core_obj._is_series_like and other_obj._is_series_like
            self._is_dataframe_like = core_obj._is_dataframe_like or other_obj._is_dataframe_like
            if left._is_series_like and right._is_series_like:
                left_script = left._get_data_select_list()[0]
                right_script = right._get_data_select_list()[0]
                self._data_select_list = [f"{func}({left_script},{right_script})"]
            elif left._is_series_like and right._is_dataframe_like:
                left_script = left._get_data_select_list()[0]
                right_scripts = right._get_data_select_list()
                self._data_select_list = [f"{func}({left_script},{right_script}"
                                         for right_script in right_scripts]
            elif left._is_dataframe_like and right._is_series_like:
                left_scripts = left._get_data_select_list()
                right_script = right._get_data_select_list()[0]
                self._data_select_list = [f"{func}({left_script},{right_script})"
                                         for left_script in left_scripts]
            elif left._is_dataframe_like and right._is_dataframe_like:
                left_scripts = left._get_data_select_list()
                right_scripts = right._get_data_select_list()
                self._data_select_list = [f"{func}({left_script},{right_script})"
                                          for left_script, right_script
                                          in zip(left_scripts, right_scripts)]
            else:
                raise TypeError("Left and right operands must be of Series or DataFrame type")

    @classmethod
    def _raw_merge_expression(cls, session, from_clause, left_var_name, right_var_name,
                              index_columns, data_select_list, ddb_dtypes,
                              index_map, data_columns, where_expr):
        assert len(data_select_list) == len(data_columns)
        assert len(data_columns) == len(ddb_dtypes)
        obj = cls.__new__(cls)
        obj._session = session
        obj._from_clause = from_clause
        obj._left_var_name = left_var_name
        obj._right_var_name = right_var_name
        obj._index_columns = index_columns
        obj._data_select_list = data_select_list
        obj._ddb_dtypes = ddb_dtypes
        obj._index_map = index_map
        obj._data_columns = data_columns
        obj._where_expr = where_expr
        obj._is_series_like = False
        obj._is_dataframe_like = True
        obj._func = obj._left = obj._right = obj._index = obj._name = None

        return obj

    @classmethod
    def _copy_with_columns_kept(cls, expr, keys=None, where_expr=None):
        obj = cls.__new__(cls)
        obj._left = expr._left
        obj._right = expr._right
        obj._from_clause = expr._from_clause
        obj._index_columns = expr._index_columns
        obj._ddb_dtypes = expr._ddb_dtypes
        obj._left_var_name = expr._left_var_name
        obj._right_var_name = expr._right_var_name
        obj._index_map = expr._index_map
        obj._session = expr._session
        obj._func = expr._func
        obj._index = expr._index
        obj._name = expr._name
        
        if keys is not None:
            if len(keys) == 1:
                obj._is_series_like = True
                obj._is_dataframe_like = False
            else:
                obj._is_series_like = False
                obj._is_dataframe_like = True
            obj._data_select_list = [col for col, data_col in zip(expr._data_select_list, expr._data_columns)
                                     if data_col in keys]
            obj._data_columns = keys
        else:
            obj._is_series_like = expr._is_series_like
            obj._is_dataframe_like = expr._is_dataframe_like
            obj._data_select_list = expr._data_select_list
            obj._data_columns = expr._data_columns

        if where_expr is not None:
            obj._where_expr = where_expr
        else:
            obj._where_expr = expr._where_expr
        return obj

    def compute(self):
        data_script = (f"{column} as {data_column}"
                       for column, data_column in zip(self._data_select_list, self._data_columns))
        select_list = itertools.chain(self._index_columns, data_script)
        script = sql_select(select_list, self._from_clause, self._where_expr)
        return get_orca_obj_from_script(self._session, script, index_map=self._index_map)

    def to_pandas(self):
        return self.compute().to_pandas()

    def _get_data_select_list(self):
        return self._data_select_list

    def __getattr__(self, key: str):
        if key in self._data_columns:
            return self[key]
        else:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{key}'")

    def __getitem__(self, key):
        if (isinstance(key, BooleanMergeExpression)
                and key._left_var_name == self._left_var_name
                and key._right_var_name == self._right_var_name):
            where_expr = _merge_where_expr(self._where_expr, key)
            return self._copy_with_columns_kept(self, where_expr=where_expr)
        else:
            keys, _ = check_key_existence(key, self._data_columns)
            return self._copy_with_columns_kept(self, keys)

    def __setitem__(self, key, value):
        _raise_must_compute_error("Setting a value to an Expression is not supported")

    def _unary_op(self, func, numeric_only):
        return ArithMergeExpression(self, None, func, 0)

    def _binary_op(self, other, func):
        return _get_expr_with_binary_op(ArithMergeExpression, self, other, func)

    def _binary_agg_op(self, other, func):
        raise NotImplementedError()

    def _extended_binary_op(self, other, func, axis, level, fill_value):
        raise NotImplementedError()

    def _unary_agg_op(self, func, axis, level, numeric_only):
        raise NotImplementedError()

    def _logical_op(self, other, func):
        return _get_expr_with_binary_op(BooleanMergeExpression, self, other, func)

    def _logical_unary_op(self, func):
        return BooleanMergeExpression(self, None, func, 0)


class ArithMergeExpression(MergeExpression):

    pass


class BooleanMergeExpression(MergeExpression):

    def _to_where_list(self):
        return self._data_select_list
