import numpy

from .common import _unary_op


def linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=None,
             axis=0):
    return numpy.linspace(start, stop, num=num, endpoint=endpoint, retstep=retstep, dtype=dtype)


def logspace(start, stop, num=50, endpoint=True, base=10.0, dtype=None,
             axis=0):
    return numpy.logspace(start, stop, num=num, endpoint=endpoint, base=base, dtype=dtype, axis=axis)


def geomspace(start, stop, num=50, endpoint=True, dtype=None, axis=0):
    return numpy.geomspace(start, stop, num=num, endpoint=endpoint, dtype=dtype, axis=axis)


def digitize(x, bins, right=False):
    return _unary_op("digitize", x, orca_support=False, bins=bins, right=right)
