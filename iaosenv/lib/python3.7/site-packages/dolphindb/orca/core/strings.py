import itertools

from numpy import nan

from .utils import to_dolphindb_literal


def _orca_unary_op(func):
    def ufunc(self):
        return self._unary_op(func)
    return ufunc

def _orca_logical_unary_op(func):
    def ufunc(self):
        return self._logical_unary_op(func)
    return ufunc


class StringMethods(object):

    def __init__(self, s):
        self._s = s

    def count(self, pat, flags=0, **kwargs):
        # count => "regexCount"
        if not isinstance(pat, str):
            raise TypeError("pat must be str type")

        if flags != 0:
            raise ValueError("Orca not support flags is not zero")
        pat = to_dolphindb_literal(pat)
        return self._unary_op(f"regexCount{{,{pat}}}")

    def decode(self, encoding, errors="strict"):
        raise NotImplementedError

    def encode(self, encoding, errors="strict"):
        raise NotImplementedError

    def endswith(self, pat, na=nan):
        if not isinstance(pat, str):
            raise TypeError("pat must be str type")
        if na is not nan:
            raise ValueError("Orca na must be nan")
        pat = to_dolphindb_literal(pat)
        return self._logical_unary_op(f"endsWith{{,{pat}}}")

    def startswith(self, pat, na=nan):
        if not isinstance(pat, str):
            raise TypeError("pat must be str type")
        if na is not nan:
            raise ValueError("Orca na must be nan")
        pat = to_dolphindb_literal(pat)
        return self._logical_unary_op(f"startsWith{{,{pat}}}")

    def find(self, sub, start=0, end=None):
        if end is not None:
            raise ValueError("orca not support end is not None")
        sub = to_dolphindb_literal(sub)
        return self._unary_op(f"regexFind{{,{sub},{start}}}")

    def get(self, i):
        if not isinstance(i,int):
            raise TypeError("i must be int type")
        # return self._unary_op(f"charAt{{,{i}}}")
        return self._unary_op(f"(x->charAt(x,{i}).string())")

    def index(self, sub, start=0, end=None):
        # TODO: if not found raise ValueError, find will return -1
        # we just set index as alias of find
        return self.find(sub,start,end)

    def slice(self, start=None, stop=None, step=None):
        if start is None and stop is None and step is None:    # trivial case
            return self
        if step is not None:
            raise NotImplementedError("step is not implemented")

        if start is None:
            start = 0
        elif not isinstance(start, int):
            raise TypeError("start must be an integer")
        elif start < 0:
            raise NotImplementedError("start must be non-negative")

        if stop is None:
            stop = ""
        elif not isinstance(stop, int):
            raise TypeError("stop must be an integer")
        elif stop < 0:
            raise NotImplementedError("stop must be non-negative")
        else:
            stop = stop - start

        return self._unary_op(f"substr{{,{start},{stop}}}")

    len = _orca_unary_op("strlen")

    def ljust(self, width, fillchar=' '):
        fillchar = to_dolphindb_literal(fillchar)
        return self._unary_op(f"rpad{{,{width},{fillchar}}}")

    lower = _orca_unary_op("lower")
    upper = _orca_unary_op("upper")

    def rjust(self, width, fillchar=' '):
        fillchar = to_dolphindb_literal(fillchar)
        return self._unary_op(f"lpad{{,{width},{fillchar}}}")

    def replace(self, pat, repl, n=-1, case=None, flags=0, regex=True):
        if regex:
            n = 0 if n == -1 else n
            return self._unary_op(f"regexReplace{{,{pat},{repl},{n}}}")
        # TODO: case sensitive
        if n != -1 or case is False or flags != 0:
            raise ValueError("Unsupport params, params must be: n=-1,case=None, flags=0")
        return self._unary_op(f"strReplace{{,{pat},{repl}}}")

    # rfind = _orca_unary_op("regexFind")  ->from the right
    # rindex = _orca_unary_op("regexFind")
    def strip(self, to_strip=None):
        if to_strip is not None:
            raise ValueError("orca to_strip must be None")
        return self._unary_op("strip")

    isalnum = _orca_logical_unary_op("isAlNum")
    isalpha = _orca_logical_unary_op("isAlpha")
    isdigit = _orca_logical_unary_op("isDigit")
    isspace = _orca_logical_unary_op("isSpace")
    islower = _orca_logical_unary_op("isLower")
    isupper = _orca_logical_unary_op("isUpper")
    istitle = _orca_logical_unary_op("isTitle")
    isnumeric = _orca_logical_unary_op("isNumeric")
    isdecimal = _orca_logical_unary_op("isDecimal")

    def _logical_unary_op(self, func):
        from .operator import BooleanExpression
        return BooleanExpression(self._s, None, func, 1)

    def _unary_op(self, func):
        from .operator import ArithExpression
        return ArithExpression(self._s, None, func, 0)
