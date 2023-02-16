import numpy as np

from .utils import (
    _NUMPY_FUNCTION_TO_ORCA_FUNCTION, _NUMPY_FUNCTION_TO_ORCA_FUNCTION_NDARRAY,
    _NUMPY_FUNCTION_TO_ORCA_REV_FUNCTION, _NUMPY_AGG_FUNCTION_TO_ORCA_FUNCTION,
    is_orca_object)


def _unary_op(func, x, orca_support=True, *args, **kwargs):
    # orca has the same func name with numpy
    if is_orca_object(x):
        if callable(orca_support):
            return orca_support(x, *args, **kwargs)
        elif orca_support:
            func_name = _NUMPY_FUNCTION_TO_ORCA_FUNCTION.get(func)
            if func_name is not None:
                return getattr(x.__class__, func_name)(x, *args, **kwargs)
            else:
                return getattr(x.__class__, func)(x, *args, **kwargs)
        else:
            return np.__dict__[func](x.to_numpy(), *args, **kwargs)
    else:
        result = np.__dict__[func](x, *args, **kwargs)
    return result


_UNARY_AGG_OP_KEYWORDS = (
    "dtype", "out", "keepdims", "where", "initial", "ddof"
)


def _unary_agg_op(func, x, orca_support=True, *args, **kwargs):
    # orca has the same func name with numpy
    if is_orca_object(x):
        if orca_support:
            func_name = _NUMPY_AGG_FUNCTION_TO_ORCA_FUNCTION.get(func)
            if func_name is not None:
                for k in _UNARY_AGG_OP_KEYWORDS:    # TODO: a better way?
                    if k in kwargs:
                        kwargs.pop(k)
                return getattr(x.__class__, func_name)(x, *args, **kwargs)
            else:
                return getattr(x.__class__, func)(x, *args, **kwargs)
        else:
            return np.__dict__[func](x.to_numpy(), *args, **kwargs)
    else:
        result = np.__dict__[func](x, *args, **kwargs)
    return result


def _binary_op(func, x1, x2, orca_support=True, *args, **kwargs):
    if is_orca_object(x1) and orca_support:
        func_name = _NUMPY_FUNCTION_TO_ORCA_FUNCTION.get(func)
        klass = x1.__class__
        if func_name is not None:
            result = getattr(klass, func_name)(x1, x2, *args, **kwargs)
        else:
            result = getattr(klass, func)(x1, x2, *args, **kwargs)
    elif is_orca_object(x2) and orca_support:
        func_name = _NUMPY_FUNCTION_TO_ORCA_REV_FUNCTION.get(func)
        klass = x2.__class__
        if func_name is not None:
            result = getattr(klass, func_name)(x2, x1, *args, **kwargs)
        else:
            result = getattr(klass, func)(x2, x1, *args, **kwargs)
    else:
        result = np.__dict__[func](x1, x2, *args, **kwargs)

    return result
