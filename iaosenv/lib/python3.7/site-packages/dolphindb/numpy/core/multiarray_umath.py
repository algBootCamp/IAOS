import numpy as np
import orca
from .common import _binary_op, _unary_op, _unary_agg_op
from .utils import is_orca_object


def add_docstring(obj, docstring):
    pass

'''
Universal functions 
'''

# Math operations
def add(x1, x2, *args, **kwargs):
    return _binary_op("add", x1, x2, *args, **kwargs)


def subtract(x1, x2, *args, **kwargs):
    return _binary_op("subtract", x1, x2, *args, **kwargs)


def multiply(x1, x2, *args, **kwargs):
    return _binary_op("multiply", x1, x2, *args, **kwargs)


def divide(x1, x2, *args, **kwargs):
    return _binary_op("divide",x1, x2, *args, **kwargs)


def logaddexp(x1, x2, *args, **kwargs):
    return _binary_op("logaddexp",  x1, x2, orca_support=False, *args, **kwargs)


def logaddexp2(x1, x2, *args, **kwargs):
    return _binary_op("logaddexp2",  x1, x2, orca_support=False, *args, **kwargs)


def true_divide(x1, x2, *args, **kwargs):
    return _binary_op("true_divide", x1, x2, *args, **kwargs)


def floor_divide(x1, x2, *args, **kwargs):
    return _binary_op("floor_divide", x1, x2, *args, **kwargs)


def negative(x, *args, **kwargs):
    return _unary_op("negative", x, *args, **kwargs)


def positive(x, *args, **kwargs):
    return _unary_op("positive", x, *args, **kwargs)


def power(x1, x2, *args, **kwargs):
    return _binary_op("power", x1, x2, *args, **kwargs)


def remainder(x1, x2, *args, **kwargs):
    return _binary_op("mod",  x1, x2, *args, **kwargs)


def mod(x1, x2, *args, **kwargs):
    return _binary_op("mod",  x1, x2, *args, **kwargs)


def fmod(x1, x2, *args, **kwargs):
    return _binary_op("fmod",  x1, x2, *args, **kwargs)


def divmod(x1, x2, *args, **kwargs):
    return _binary_op("divmod", x1, x2, *args, **kwargs)


def absolute(x, *args, **kwargs):
    return _unary_op("absolute", x, *args, **kwargs)


abs = absolute


def fabs(x, *args, **kwargs):
    return _unary_op("fabs", x, orca_support=False, *args, **kwargs)


def rint(x, *args, **kwargs):
    return _unary_op("rint", x, *args, **kwargs)


def sign(x, *args, **kwargs):
    return _unary_op("sign", x, orca_support=False, *args, **kwargs)


def heaviside(x, *args, **kwargs):
    return _unary_op("heaviside", x, orca_support=False, *args, **kwargs)


def conj(x, *args, **kwargs):
    return _unary_op("conjugate", x, orca_support=False, *args, **kwargs)


def conjugate(x, *args, **kwargs):
    return _unary_op("conjugate", x, orca_support=False, *args, **kwargs)


def exp(x, *args, **kwargs):
    return _unary_op("exp", x, *args, **kwargs)


def exp2(x, *args, **kwargs):
    return _unary_op("exp2", x, *args, **kwargs)


def log(x, *args, **kwargs):
    return _unary_op("log", x, *args, **kwargs)


def log2(x, *args, **kwargs):
    return _unary_op("log2", x, *args, **kwargs)


def log10(x, *args, **kwargs):
    return _unary_op("log10", x, *args, **kwargs)


def expm1(x, *args, **kwargs):
    return _unary_op("expm1", x, *args, **kwargs)


def log1p(x, *args, **kwargs):
    return _unary_op("log1p", x, *args, **kwargs)


def sqrt(x, *args, **kwargs):
    return _unary_op("sqrt", x, *args, **kwargs)


def square(x, *args, **kwargs):
    return _unary_op("square", x, *args, **kwargs)


def cbrt(x, *args, **kwargs):
    return _unary_op("cbrt", x, *args, **kwargs)


def reciprocal(x, *args, **kwargs):
    return _unary_op("reciprocal", x, *args, **kwargs)


def gcd(x1, x2, *args, **kwargs):
    return _binary_op("gcd", x1, x2, orca_support=False, *args, **kwargs)


def lcm(x1, x2, *args, **kwargs):
    return _binary_op("lcm", x1, x2, orca_support=False, *args, **kwargs)


# Trigonometric functions
def sin(x, *args, **kwargs):
    return _unary_op("sin", x, *args, **kwargs)


def cos(x, *args, **kwargs):
    return _unary_op("cos", x, *args, **kwargs)


def tan(x, *args, **kwargs):
    return _unary_op("tan", x, *args, **kwargs)


def arcsin(x, *args, **kwargs):
    return _unary_op("arcsin", x, *args, **kwargs)


def arccos(x, *args, **kwargs):
    return _unary_op("arccos", x, *args, **kwargs)


def arctan(x, *args, **kwargs):
    return _unary_op("arctan", x, *args, **kwargs)


def arctan2(x1, x2, *args, **kwargs):
    return _binary_op("arctan2",  x1, x2, orca_support=False, *args, **kwargs)


def hypot(x, *args, **kwargs):
    return _unary_op("hypot", x, orca_support=False, *args, **kwargs)


def sinh(x, *args, **kwargs):
    return _unary_op("sinh", x, *args, **kwargs)


def cosh(x, *args, **kwargs):
    return _unary_op("cosh", x, *args, **kwargs)


def tanh(x, *args, **kwargs):
    return _unary_op("tanh", x, *args, **kwargs)


def arcsinh(x, *args, **kwargs):
    return _unary_op("arcsinh", x, *args, **kwargs)


def arccosh(x, *args, **kwargs):
    return _unary_op("arccosh", x, *args, **kwargs)


def arctanh(x, *args, **kwargs):
    return _unary_op("arctanh", x, *args, **kwargs)


def deg2rad(x, *args, **kwargs):
    return _unary_op("deg2rad", x, *args, **kwargs)


def rad2deg(x, *args, **kwargs):
    return _unary_op("rad2deg", x, *args, **kwargs)


# Bit-twiddling functions

def bitwise_and(x1, x2, *args, **kwargs):
    return _binary_op("bitwise_and", x1, x2, *args, **kwargs)


def bitwise_or(x1, x2, *args, **kwargs):
    return _binary_op("bitwise_or", x1, x2, *args, **kwargs)


def bitwise_xor(x1, x2, *args, **kwargs):
    return _binary_op("bitwise_xor", x1, x2, *args, **kwargs)


def invert(x, *args, **kwargs):
    return _unary_op("invert", x, *args, **kwargs)


def left_shift(x1, x2, *args, **kwargs):
    return _binary_op("left_shift",  x1, x2, *args, **kwargs)


def right_shift(x1, x2, *args, **kwargs):
    return _binary_op("right_shift",  x1, x2, *args, **kwargs)


# Comparison functions
def greater(x1, x2, *args, **kwargs):
    return _binary_op("greater", x1, x2, *args, **kwargs)


def greater_equal(x1, x2, *args, **kwargs):
    return _binary_op("greater_equal", x1, x2, *args, **kwargs)


def less(x1, x2, *args, **kwargs):
    return _binary_op("less", x1, x2, *args, **kwargs)


def less_equal(x1, x2, *args, **kwargs):
    return _binary_op("less_equal", x1, x2, *args, **kwargs)


def not_equal(x1, x2, *args, **kwargs):
    return _binary_op("not_equal", x1, x2, *args, **kwargs)


def equal(x1, x2, *args, **kwargs):
    return _binary_op("equal", x1, x2, *args, **kwargs)


def logical_and(x1, x2, *args, **kwargs):
    return _binary_op("logical_and", x1, x2, *args, **kwargs)


def logical_or(x1, x2, *args, **kwargs):
    return _binary_op("logical_or", x1, x2, *args, **kwargs)


def logical_xor(x1, x2, *args, **kwargs):
    return _binary_op("logical_xor", x1, x2, *args, **kwargs)


def logical_not(x, *args, **kwargs):
    return _unary_op("logical_not", x, *args, **kwargs)


def maximum(x1, x2, *args, **kwargs):
    return _binary_op("maximum", x1, x2, *args, **kwargs)


def minimum(x1, x2, *args, **kwargs):
    return _binary_op("minimum", x1, x2, *args, **kwargs)


def fmax(x1, x2, *args, **kwargs):
    return _binary_op("fmax", x1, x2, *args, **kwargs)


def fmin(x1, x2, *args, **kwargs):
    return _binary_op("fmin", x1, x2, *args, **kwargs)


# Floating functions

def isfinite(x, *args, **kwargs):
    return _unary_op("isfinite", x, orca_support=False, *args, **kwargs)


def isinf(x, *args, **kwargs):
    return _unary_op("isinf", x, orca_support=False, *args, **kwargs)


def isnan(x, *args, **kwargs):
    return _unary_op("isnan", x, orca_support=False, *args, **kwargs)


def isnat(x, *args, **kwargs):
    return _unary_op("isnat", x, orca_support=False, *args, **kwargs)


def signbit(x, *args, **kwargs):
    return _unary_op("signbit", x, orca_support=False, *args, **kwargs)


def copysign(x1, x2, *args, **kwargs):
    return _binary_op("copysign",  x1, x2, orca_support=False, *args, **kwargs)


def nextafter(x1, x2, *args, **kwargs):
    return _binary_op("nextafter",  x1, x2, orca_support=False, *args, **kwargs)


def spacing(x, *args, **kwargs):
    return _unary_op("spacing", x, orca_support=False, *args, **kwargs)


def modf(x, *args, **kwargs):
    return _unary_op("modf", x, orca_support=False, *args, **kwargs)


def ldexp(x1, x2, *args, **kwargs):
    return _binary_op("ldexp", x1, x2, orca_support=False, *args, **kwargs)


def frexp(x, out1=None, out2=None, *args, **kwargs):
    return _unary_op("frexp", x, orca_support=False, out1=out1, out2=out2, *args, **kwargs)


def floor(x, *args, **kwargs):
    return _unary_op("floor", x, *args, **kwargs)


def ceil(x, *args, **kwargs):
    return _unary_op("ceil", x, *args, **kwargs)


def trunk(x, *args, **kwargs):
    return _unary_op("trunk", x, *args, **kwargs)


def bincount(x, weights=None, minlength=0):
    return _unary_op("bincount", x, orca_support=False, weights=weights, minlength=minlength)


def busday_count(begindates, enddates, weekmask='1111100', holidays=[], busdaycal=None,
                 out=None):
    return np.busday_count(begindates, enddates, weekmask=weekmask, holidays=holidays, busdaycal=busdaycal,
                           out=out)


def busday_offset(dates, offsets, roll='raise', weekmask='1111100', holidays=None, busdaycal=None,
                  out=None):
    return np.busday_offset(dates, offsets, roll=roll, weekmask=weekmask, holidays=holidays, busdaycal=busdaycal,
                            out=out)


def can_cast(from_, to, casting='safe'):
    return np.can_cast(from_, to, casting=casting)


def clip(x1, x2, x3, *args, **kwargs):
    if isinstance(x1, (orca.DataFrame, orca.Series)):
        return x1.clip(x2, x3, *args, **kwargs)
    else:
        return np.clip(x1, x2, x3, *args, **kwargs)


def compare_chararrays(a, b, cmp_op, rstrip):
    if isinstance(a, (orca.DataFrame, orca.Series)):
        return np.compare_chararrays(a.to_numpy(), b.to_numpy(), cmp_op, rstrip)
    else:
        return np.compare_chararrays(a, b, cmp_op, rstrip)


def concatenate(arrays, axis=0, out=None):
    for i in range(len(arrays)):
        if isinstance(arrays[i], (orca.DataFrame, orca.Series, np.ndarray)):
            arrays[i] = arrays[i].to_numpy()
    return np.concatenate(arrays, axis=axis, out=out)


def copyto(dst, src, casting='same_kind', where=True):
    return _binary_op("copyto", dst, src,  orca_support=False, casting=casting, where=where)


def count_nonzero(a, axis=None):
    return _unary_op("count_nonzero",  a, orca_support=False, axis=axis)


def datetime_as_string(arr, unit=None, timezone='naive',
                       casting='same_kind'):
    return _unary_op("datetime_as_string",  arr, orca_support=False, unit=unit, timezone=timezone,
                                                               casting=casting)


def datetime_data(dtype, *args, **kwargs):
    return _unary_op("datetime_data", dtype, orca_support=False,  *args, **kwargs)


def degrees(x, *args, **kwargs):
    return _unary_op("degrees", x, orca_support=False, *args, **kwargs)


def dot(a, b, out=None):
    return _binary_op("dot", a, b, orca_support=False, out=out)


def empty_like(prototype, dtype=None, order='K', subok=True,
               shape=None):
    return _unary_op("empty_like", prototype, dtype=dtype, order=order, subok=subok,
                                   shape=shape)


def float_power(x1, x2, *args, **kwargs):
    return _binary_op("float_power",  x1, x2, orca_support=False, *args, **kwargs)


# unary aggregate op

def sum(a, axis=None, dtype=None, out=None, keepdims=np._NoValue, initial=np._NoValue, where=np._NoValue):
    return _unary_agg_op("sum", a, axis=axis, dtype=dtype, out=out, keepdims=keepdims, initial=initial, where=where)


def amin(a, axis=None, out=None, keepdims=np._NoValue, initial=np._NoValue,
         where=np._NoValue):
    return _unary_agg_op("amin", a, axis=axis, out=out, keepdims=keepdims, initial=initial, where=where)


def amax(a, axis=None, out=None, keepdims=np._NoValue, initial=np._NoValue,
         where=np._NoValue):
    return _unary_agg_op("amax", a, axis=axis, out=out, keepdims=keepdims, initial=initial, where=where)


def nanmin(a, axis=None, out=None, keepdims=np._NoValue):
    return _unary_agg_op("nanmin", a, axis=axis, out=out, keepdims=keepdims)


def nanmax(a, axis=None, out=None, keepdims=np._NoValue):
    return _unary_agg_op("nanmax", a, axis=axis, out=out, keepdims=keepdims)


def ptp(a, axis=None, out=None, keepdims=np._NoValue):
    return _unary_agg_op("ptp", a, orca_support=False, axis=axis, out=out, keepdims=keepdims)


def percentile(a, axis=None, out=None,
               overwrite_input=False, interpolation='linear', keepdims=False):
    return _unary_agg_op("percentile", a, orca_support=False,
                         axis=axis, out=out, overwrite_input=overwrite_input,
                         interpolation=interpolation, keepdims=keepdims)


def nanpercentile(a, axis=None, out=None,
                  overwrite_input=False, interpolation='linear', keepdims=False):
    return _unary_agg_op("nanpercentile", a, orca_support=False,
                         axis=axis, out=out, overwrite_input=overwrite_input,
                         interpolation=interpolation, keepdims=keepdims)


def quantile(a, axis=None, out=None,
             overwrite_input=False, interpolation='linear', keepdims=False):
    return _unary_agg_op("quantile", a, axis=axis, out=out,
                         overwrite_input=overwrite_input,
                         interpolation=interpolation, keepdims=keepdims)


def nanquantile(a, axis=None, out=None,
                overwrite_input=False, interpolation='linear', keepdims=False):
    return _unary_agg_op("nanquantile", a, axis=axis, out=out,
                         overwrite_input=overwrite_input,
                         interpolation=interpolation, keepdims=keepdims)


# Averages and variances
def median(a, axis=None, out=None, overwrite_input=False, keepdims=False):
    return _unary_agg_op("median", a, axis=axis, out=out,
                         overwrite_input=overwrite_input, keepdims=keepdims)


def average(a, axis=None, weights=None, returned=False):
    return _unary_agg_op("average", a, axis=axis, weights=weights, returned=returned)


def mean(a, axis=None, dtype=None, out=None, keepdims=False):
    return _unary_agg_op("mean", a, axis=axis, dtype=dtype, out=out, keepdims=keepdims)


def std(a, axis=None, dtype=None, out=None, ddof=0, keepdims=False):
    # TODO: support ddof
    return _unary_agg_op("std", a, axis=axis, dtype=dtype, out=out, ddof=ddof, keepdims=keepdims)


def var(a, axis=None, dtype=None, out=None, ddof=0, keepdims=False):
    # TODO: support ddof
    return _unary_agg_op("var", a, axis=axis, dtype=dtype, out=out, ddof=ddof, keepdims=keepdims)


def nanmedian(a, axis=None, out=None,
              overwrite_input=False, keepdims=False):
    return _unary_agg_op("nanmedian", a, axis=axis, out=out, overwrite_input=overwrite_input, keepdims=keepdims)


def nanmean(a, axis=None, dtype=None, out=None, keepdims=False):
    return _unary_agg_op("nanmean", a, axis=axis, dtype=dtype, out=out, keepdims=keepdims)


def nanstd(a, axis=None, dtype=None, out=None, ddof=0, keepdims=False):
    return _unary_agg_op("nanstd", a, axis=axis, dtype=dtype, out=out, ddof=ddof, keepdims=keepdims)


def nanvar(a, axis=None, dtype=None, out=None, ddof=0, keepdims=False):
    return _unary_agg_op("nanstd", a, axis=axis, dtype=dtype, out=out, ddof=ddof, keepdims=keepdims)


# Correlating
def corrcoef(x, y=None, rowvar=True, bias=np._NoValue, ddof=np._NoValue):
    return _binary_op("corrcoef", x, y, orca_support=False, rowvar=rowvar, bias=bias, ddof=ddof)


def correlate(a, v, mode='valid'):
    return _binary_op("correlate", a, v, orca_support=False, mode=mode)


def cov(m, y=None, rowvar=True, bias=False, ddof=None, fweights=None,
        aweights=None):
    return _binary_op("cov", m, y, orca_support=False,
                      rowvar=rowvar, bias=bias, ddof=ddof,
                      fweights=fweights, aweights=aweights)

def where(condition, x=None, y=None):
    # TODO: this could be inefficient when combined with UPDATE
    if is_orca_object(condition):
        condition = condition.to_pandas()
    if is_orca_object(x):
        x = x.to_pandas()
    if is_orca_object(y):
        y = y.to_pandas()
    return np.where(condition, x, y)