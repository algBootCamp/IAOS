import numpy as np

import orca


_NUMPY_FUNCTION_TO_ORCA_FUNCTION_NDARRAY = {
    "__sub__": "__rsub__",
    "__add__": "__radd__",
    "__mul__": "__rmul__",
    "__div__": "__rdiv__",
    "__truediv__": "__rtruediv__",
    "__floordiv__": "__rfloordiv__",
    "__mod__": "__rmod__",
    "__pow__": "__rpow__",
    "__divmod__": "__rdivmod__",
    "__lshift__": "__rlshift__",
    "__rshift__": "__rrshift__",

    "__and__": "__and__",
    "__or__": "__or__",
    "__xor__": "logical_xor",
    "__gt__": "__lt__",
    "__ge__": "__le__",
    "__lt__": "__gt__",
    "__le__": "__ge__",
    "__eq__": "__eq__",
    "__ne__": "__ne__",
}


_NUMPY_FUNCTION_TO_ORCA_FUNCTION = {
    "subtract": "sub",
    "multiply": "mul",
    "divide": "div",
    "true_divide": "truediv",
    "negative": "__neg__",
    "positive": "__pos__",
    "power": "pow",
    "mod": "mod",
    "fmod": "mod",
    "divmod": "divmod",
    "left_shift": "lshift",
    "right_shift": "rshift",

    "absolute": "abs",
    "rint": "round",

    "bitwise_xor": "__xor__",
    "invert": "bitwise_not",
    "greater": "gt",
    "greater_equal": "ge",
    "less": "lt",
    "less_equal": "le",
    "not_equal": "ne",
    "equal": "eq",
    "logical_and": "__and__",
    "logical_or": "__or__",
    "logical_not": "invert",
    "floor_divide": "floordiv",
    "trunc": "truncate",

    "amin": "min",
    "amax": "max",
    "nanquantile": "quantile",
    "nanmedian": "median",
    "nanmean": "mean",
    "nanstd": "std",
    "nanvar": "var",

    "corrcoef": "corr",
    "correlate": "corr",

    "maximum": "_fmax",
    "minimum": "_fmin",
    "fmax": "_fmax",
    "fmin": "_fmin",
}


_NUMPY_FUNCTION_TO_ORCA_REV_FUNCTION = {
    "subtract": "rsub",
    "multiply": "rmul",
    "divide": "rdiv",
    "true_divide": "rtruediv",
    "floor_divide": "rfloordiv",
    "power": "rpow",
    "mod": "rmod",
    "fmod": "rmod",
    "divmod": "rdivmod",
    "left_shift": "rlshift",
    "right_shift": "rrshift",

    "bitwise_xor": "__xor__",
    "greater": "lt",
    "greater_equal": "le",
    "less": "gt",
    "less_equal": "ge",
    "not_equal": "ne",
    "equal": "eq",
    "logical_and": "__and__",
    "logical_or": "__or__",
    "trunc": "truncate",

    "maximum": "_fmax",
    "minimum": "_fmin",
    "fmax": "_fmax",
    "fmin": "_fmin",
}


_NUMPY_AGG_FUNCTION_TO_ORCA_FUNCTION = {
    "sum": "sum",
    "amin": "min",
    "amax": "max",
    "nanmin": "min",
    "nanmax": "max",
    "percentile": "percentile",
    "nanpercentile": "nanpercentile",
    "quantile": "quantile",
    "nanquantile": "quantile",
    "median": "median",
    "average": "mean",
    "mean": "mean",
    "std": "std",
    "var": "var",
    "nanmedian": "median",
    "nanmean": "mean",
    "nanstd": "std",
    "nanvar": "var"
}


def _dnp_dtype_to_np_dtype(dnp_dtype):
    from .generic import (
        bool_, complex_, datetime64, float_, half, int8, intc, long, longcomplex,
        longfloat, longlong, object_, short, single, singlecomplex, string_,
        timedelta64, uint8, uintc, uintp, ulonglong, unicode_,
        ushort, void0)
    _DNP_DTYPE_TO_NP_DTYPE = {
        int8: np.int8,
        bool_: np.bool_,
        complex_: np.complex_,
        string_: np.string_,
        longcomplex: np.longcomplex,
        singlecomplex: np.singlecomplex,
        datetime64: np.datetime64,
        float_: np.float_,
        longfloat: np.longfloat,
        half: np.half,
        single: np.single,
        long: np.long,
        short: np.short,
        intc: np.intc,
        longlong: np.longlong,
        object_: np.object_,
        void0: np.void0,
        unicode_: np.unicode_,
        timedelta64: np.timedelta64,
        uint8: np.uint8,
        uintp: np.uintp,
        ushort: np.ushort,
        uintc: np.uintc,
        ulonglong: np.ulonglong,
    }
    return _DNP_DTYPE_TO_NP_DTYPE[dnp_dtype]


def is_orca_object(x):
    return isinstance(x, (orca.DataFrame, orca.Series,
                          orca.ArithExpression, orca.BooleanExpression,
                          orca.core.groupby.ContextByExpression))
