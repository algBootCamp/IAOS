# from numpy.core.generic import *
# import numpy as np

# from dolphindb_numpy.core.utils import _NUMPY_FUNCTION_TO_ORCA_FUNCTION_NDARRAY, _NUMPY_FUNCTION_TO_ORCA_FUNCTION, _NUMPY_FUNCTION_TO_ORCA_REV_FUNCTION
# from orca.core.frame import DataFrame
# from orca.core.series import Series


# def _np_dtype_to_dnp_dtype(np_data):    # TODO: move to utils
#     _NP_TYPE_TO_DNP_DTYPE = {
#         np.int8: int8,
#         np.bool_: bool_,
#         np.string_: string_,
#         np.complex_: complex_,
#         np.longcomplex: longcomplex,
#         np.singlecomplex: singlecomplex,
#         np.datetime64: datetime64,
#         np.float_: float_,
#         np.longfloat: longfloat,
#         np.half: half,
#         np.single: single,
#         np.long: long,
#         np.short: short,
#         np.intc: intc,
#         np.longlong: longlong,
#         np.object_: object_,
#         np.void0: void0,
#         np.unicode_: unicode_,
#         np.datetime64: datetime64,
#         np.uint8: uint8,
#         np.uintp: uintp,
#         np.ushort: ushort,
#         np.uintc: uintc,
#         np.ulonglong: ulonglong,
#         np.byte: byte,
#         np.bool8: bool8,
#         np.complex128: complex128,
#         np.cfloat: cfloat,
#         np.cdouble: cdouble,
#         # np.complex256: complex256,
#         np.clongfloat: clongfloat,
#         np.clongdouble: clongdouble,
#         np.csingle: csingle,
#         np.complex64: complex64,
#         np.float64: float64,
#         np.double: double,
#         np.longdouble: longdouble,
#         # np.float128: float128,
#         np.float16: float16,
#         np.float32: float32,
#         np.int_: int_,
#         np.intp: intp,
#         np.int64: int64,
#         np.int0: int0,
#         np.int16: int16,
#         np.int32: int32,
#         np.object0: object0,
#         np.void: void,
#         np.unicode: unicode,
#         np.str_: str_,
#         np.str0: str0,
#         np.ubyte: ubyte,
#         np.uint64: uint64,
#         np.uint0: uint0,
#         np.uint: uint,
#         np.uint16: uint16,
#         np.uint32: uint32,
#     }
#     return _NP_TYPE_TO_DNP_DTYPE[np_data.__class__]


# class dolphindb_numpy_generic(object):
#     def __init__(self):
#         pass

#     def _binary_op(self, func, other, *args, **kwargs):
#         if isinstance(other, (DataFrame, Series)):
#             if _NUMPY_FUNCTION_TO_ORCA_FUNCTION_NDARRAY.get(func) is not None:
#                 func_name = _NUMPY_FUNCTION_TO_ORCA_FUNCTION_NDARRAY[func]
#                 return getattr(other.__class__, func_name)(other, self, *args, **kwargs)
#             else:
#                 raise NotImplementedError()
#                 return getattr(other.__class__, func)(other, self, *args, **kwargs)
#         else:
#             if isinstance(other, dolphindb_numpy_generic):
#                 other = other._np_data
#             result = getattr(self._np_data, func)(other, *args, **kwargs)
#             from dolphindb_numpy.core.multiarray import ndarray
#             if (isinstance(result, np.ndarray)):
#                 return ndarray(result)
#             elif isinstance(result, np.generic):
#                 return _np_dtype_to_dnp_dtype(result)(result)
#             else:
#                 return result

#     def __abs__(self, *args, **kwargs):
#         return self.__new__(self.__class__, self._np_data.__invert__(*args, **kwargs))

#     def __add__(self, y, *args, **kwargs):
#         return self._binary_op("__add__", y, *args, **kwargs)

#     def __and__(self, y, *args, **kwargs):
#         return self._binary_op("__and__", y, *args, **kwargs)

#     def __array_function__(self, *args, **kwargs):
#         return self._np_data.__array_function__(*args, **kwargs)

#     def __array_prepare__(self, obj):
#         return self._np_data.__array_prepare__(obj)

#     def __array_ufunc__(self, *args, **kwargs):
#         return self._np_data.__array_ufunc__(*args, **kwargs)

#     def __array_wrap__(self, obj):
#         return self._np_data.__array_wrap__(obj)

#     def __array__(self, *args, **kwargs):
#         return self._np_data.__array__(*args, **kwargs)

#     def __bool__(self, *args, **kwargs):
#         return self._np_data.__bool__(*args, **kwargs)

#     def __complex__(self, *args, **kwargs):
#         return self._np_data.__complex__(*args, **kwargs)

#     def __contains__(self, *args, **kwargs):
#         return self._np_data.__contains__(*args, **kwargs)

#     def __copy__(self):
#         return self._np_data.copy()

#     def __deepcopy__(self, memo, *args, **kwargs):
#         return self._np_data.__deepcopy__(memo, *args, **kwargs)

#     def __delitem__(self, *args, **kwargs):
#         return self._np_data.__delitem__(*args, **kwargs)

#     def __divmod__(self, *args, **kwargs):
#         return self._np_data.__divmod__(*args, **kwargs)

#     def __eq__(self, y, *args, **kwargs):
#         return self._binary_op("__eq__", y, *args, **kwargs)

#     def __float__(self, *args, **kwargs):
#         return self._np_data.__float__(*args, **kwargs)

#     def __floordiv__(self, y, *args, **kwargs):
#         return self._binary_op("__floordiv__", y, *args, **kwargs)

#     def __format__(self, *args, **kwargs):
#         return self._np_data.__format__(*args, **kwargs)

#     def __getitem__(self, *args, **kwargs):
#         return self._np_data.__getitem__(*args, **kwargs)

#     def __ge__(self, y, *args, **kwargs):
#         return self._binary_op("__ge__", y, *args, **kwargs)

#     def __gt__(self, y, *args, **kwargs):
#         return self._binary_op("__gt__", y, *args, **kwargs)

#     def __iadd__(self, y, *args, **kwargs):
#         return self._binary_op("__iadd__", y, *args, **kwargs)

#     def __iand__(self, y, *args, **kwargs):
#         return self._binary_op("__iand__", y, *args, **kwargs)

#     def __ifloordiv__(self, y, *args, **kwargs):
#         return self._binary_op("__ifloordiv__", y, *args, **kwargs)

#     def __ilshift__(self, y, *args, **kwargs):
#         return self._binary_op("__ilshift__", y, *args, **kwargs)

#     def __imatmul__(self, y, *args, **kwargs):
#         return self._binary_op("__imatmul__", y, *args, **kwargs)

#     def __imod__(self, y, *args, **kwargs):
#         return self._binary_op("__imod__", y, *args, **kwargs)

#     def __imul__(self, y, *args, **kwargs):
#         return self._binary_op("__imul__", y, *args, **kwargs)

#     def __ior__(self, y, *args, **kwargs):
#         return self._binary_op("__ior__", y, *args, **kwargs)

#     def __ipow__(self, y, *args, **kwargs):
#         return self._binary_op("__ipow__", y, *args, **kwargs)

#     def __isub__(self, y, *args, **kwargs):
#         return self._binary_op("__isub__", y, *args, **kwargs)

#     def __itruediv__(self, y, *args, **kwargs):
#         return self._binary_op("__itruediv__", y, *args, **kwargs)

#     def __ixor__(self, y, *args, **kwargs):
#         return self._binary_op("__ixor__", y, *args, **kwargs)

#     def __len__(self, *args, **kwargs):
#         return self._np_data.__len__(*args, **kwargs)

#     def __le__(self, y, *args, **kwargs):
#         return self._binary_op("__le__", y, *args, **kwargs)

#     def __lshift__(self, *args, **kwargs):
#         return self._np_data.__lshift__(*args, **kwargs)

#     def __lt__(self, y, *args, **kwargs):
#         return self._binary_op("__lt__", y, *args, **kwargs)

#     def __matmul__(self, *args, **kwargs):
#         return self._np_data.__matmul__(*args, **kwargs)

#     def __mod__(self, y, *args, **kwargs):
#         return self._binary_op("__mod__", y, *args, **kwargs)

#     def __mul__(self, y, *args, **kwargs):
#         return self._binary_op("__mul__", y, *args, **kwargs)

#     def __neg__(self, *args, **kwargs):
#         return self.__new__(self.__class__, self._np_data.__invert__(*args, **kwargs))

#     def __ne__(self, y, *args, **kwargs):
#         return self._binary_op("__ne__", y, *args, **kwargs)

#     def __or__(self, y, *args, **kwargs):
#         return self._binary_op("__or__", y, *args, **kwargs)

#     def __pos__(self, *args, **kwargs):
#         return self._np_data.__pos__(*args, **kwargs)

#     def __pow__(self, y, *args, **kwargs):
#         return self._binary_op("__pow__", y, *args, **kwargs)

#     def __radd__(self, *args, **kwargs):
#         return self.__new__(self.__class__, self._np_data.__radd__(*args, **kwargs))

#     def __rand__(self, *args, **kwargs):
#         return self.__new__(self.__class__, self._np_data.__rand__(*args, **kwargs))

#     def __rdivmod__(self, *args, **kwargs):
#         return self.__new__(self.__class__, self._np_data.__rdivmod__(*args, **kwargs))

#     def __reduce_ex__(self, *args, **kwargs):
#         return self.__new__(self.__class__, self._np_data.__reduce_ex__(*args, **kwargs))

#     def __reduce__(self):
#         return self._np_data.__reduce__()

#     def __repr__(self, *args, **kwargs):
#         return self._np_data.__repr__(*args, **kwargs)

#     def __rfloordiv__(self, *args, **kwargs):
#         return self.__new__(self.__class__, self._np_data.__rfloordiv__(*args, **kwargs))

#     def __rlshift__(self, *args, **kwargs):
#         return self.__new__(self.__class__, self._np_data.__rlshift__(*args, **kwargs))

#     def __rmatmul__(self, *args, **kwargs):
#         return self.__new__(self.__class__, self._np_data.__rmatmul__(*args, **kwargs))

#     def __rmod__(self, *args, **kwargs):
#         return self.__new__(self.__class__, self._np_data.__rmod__(*args, **kwargs))

#     def __rmul__(self, *args, **kwargs):
#         return self.__new__(self.__class__, self._np_data.__rmul__(*args, **kwargs))

#     def __ror__(self, *args, **kwargs):
#         return self.__new__(self.__class__, self._np_data.__ror__(*args, **kwargs))

#     def __rpow__(self, *args, **kwargs):
#         return self.__new__(self.__class__, self._np_data.__rpow__(*args, **kwargs))

#     def __rrshift__(self, *args, **kwargs):
#         return self.__new__(self.__class__, self._np_data.__rrshift__(*args, **kwargs))

#     def __rshift__(self, *args, **kwargs):
#         return self.__new__(self.__class__, self._np_data.__rshift__(*args, **kwargs))

#     def __rsub__(self, *args, **kwargs):
#         return self.__new__(self.__class__, self._np_data.__rsub__(*args, **kwargs))

#     def __rtruediv__(self, *args, **kwargs):
#         return self.__new__(self.__class__, self._np_data.__rtruediv__(*args, **kwargs))

#     def __rxor__(self, *args, **kwargs):
#         return self.__new__(self.__class__, self._np_data.__rxor__(*args, **kwargs))

#     def __setitem__(self, *args, **kwargs):
#         return self._np_data.__rxor__(*args, **kwargs)

#     def __setstate__(self, state, *args, **kwargs):
#         return self._np_data.__rlshift__(*args, **kwargs)

#     def __sizeof__(self, *args, **kwargs):
#         return self._np_data.__sizeof__(*args, **kwargs)

#     def __str__(self, *args, **kwargs):
#         return self._np_data.__str__(*args, **kwargs)

#     def __sub__(self, y, *args, **kwargs):
#         return self._binary_op("__sub__", y, *args, **kwargs)

#     def __truediv__(self, y, *args, **kwargs):
#         return self._binary_op("__truediv__", y, *args, **kwargs)

#     def __xor__(self, y, *args, **kwargs):
#         return self._binary_op("__xor__", y, *args, **kwargs)

#     def __invert__(self, *args, **kwargs):
#         return self.__new__(self.__class__, self._np_data.__invert__(*args, **kwargs))

#     @property
#     def __hash__(self):
#         return self._np_data.__hash__

#     @property
#     def base(self):
#         return self._np_data.base

#     @property
#     def ctypes(self):
#         return self._np_data.ctypes

#     @property
#     def data(self):
#         return self._np_data.data

#     @property
#     def dtype(self):
#         return self._np_data.dtype

#     @property
#     def flags(self):
#         return self._np_data.flags

#     @property
#     def flat(self):
#         return self._np_data.flat

#     @property
#     def imag(self):
#         return self._np_data.imag

#     @property
#     def itemsize(self):
#         return self._np_data.itemsize

#     @property
#     def nbytes(self):
#         return self._np_data.nbytes

#     @property
#     def ndim(self):
#         return self._np_data.ndim

#     @property
#     def real(self):
#         return self._np_data.real

#     @property
#     def shape(self):
#         return self._np_data.shape

#     @property
#     def size(self):
#         return self._np_data.size

#     @property
#     def strides(self):
#         return self._np_data.strides

#     @property
#     def T(self):
#         return self._np_data.T

#     @property
#     def __array_finalize__(self):
#         return self._np_data.__array_finalize__

#     @property
#     def __array_interface__(self):
#         return self._np_data.__array_interface__

#     @property
#     def __array_priority__(self):
#         return self._np_data.__array_priority__

#     @property
#     def __array_struct__(self):
#         return self._np_data.__array_struct__

#     @property
#     def __hash__(self):
#         return self._np_data.__hash__


# class int8(dolphindb_numpy_generic):
#     def __init__(self, *args, **kwargs):
#         self._np_data = np.int8(*args, **kwargs)


# byte = int8


# class bool_(dolphindb_numpy_generic):
#     def __init__(self, *args, **kwargs):
#         self._np_data = np.bool_(*args, **kwargs)


# bool8 = bool_


# class string_(dolphindb_numpy_generic, bytes):
#     def __init__(self, *args, **kwargs):
#         self._np_data = np.bool_(*args, **kwargs)


# class complex_(dolphindb_numpy_generic, complex):
#     def __init__(self, *args, **kwargs):
#         self._np_data = np.complex_(*args, **kwargs)


# complex128 = complex_

# cfloat = complex_

# cdouble = complex_


# class longcomplex(dolphindb_numpy_generic):
#     def __init__(self, *args, **kwargs):
#         self._np_data = np.longcomplex(*args, **kwargs)


# complex256 = longcomplex

# clongfloat = longcomplex

# clongdouble = longcomplex


# class singlecomplex(dolphindb_numpy_generic):
#     def __init__(self, *args, **kwargs):
#         self._np_data = np.singlecomplex(*args, **kwargs)


# csingle = singlecomplex

# complex64 = singlecomplex


# class datetime64(dolphindb_numpy_generic):
#     def __init__(self, *args, **kwargs):
#         self._np_data = np.datetime64(*args, **kwargs)

# class float_(dolphindb_numpy_generic, float):
#     def __init__(self, *args, **kwargs):
#         self._np_data = np.float_(*args, **kwargs)

# float64 = float_


# double = float_

# class longfloat(dolphindb_numpy_generic):
#     def __init__(self, *args, **kwargs):
#         self._np_data = np.longfloat(*args, **kwargs)

# longdouble = longfloat


# float128 = longfloat

# class half(dolphindb_numpy_generic):
#     def __init__(self, *args, **kwargs):
#         self._np_data = np.half(*args, **kwargs)

# float16 = half


# class single(dolphindb_numpy_generic):
#     def __init__(self, *args, **kwargs):
#         self._np_data = np.single(*args, **kwargs)

# float32 = single


# class long(dolphindb_numpy_generic):
#     def __init__(self, *args, **kwargs):
#         self._np_data = np.long(*args, **kwargs)


# int_ = long


# intp = long


# int64 = long


# int0 = long


# class short(dolphindb_numpy_generic):
#     def __init__(self, *args, **kwargs):
#         self._np_data = np.short(*args, **kwargs)


# int16 = short


# class intc(dolphindb_numpy_generic):
#     def __init__(self, *args, **kwargs):
#         self._np_data = np.intc(*args, **kwargs)

# int32 = intc


# class longlong(dolphindb_numpy_generic):
#     def __init__(self, *args, **kwargs):
#         self._np_data = np.longlong(*args, **kwargs)

# class object_(dolphindb_numpy_generic):
#     def __init__(self, *args, **kwargs):
#         self._np_data = np.object_(*args, **kwargs)


# object0 = object_


# class void0(dolphindb_numpy_generic):
#     def __init__(self, *args, **kwargs):
#         self._np_data = np.void0(*args, **kwargs)

# void = void0


# class unicode_(str, dolphindb_numpy_generic):
#     def __init__(self, *args, **kwargs):
#         self._np_data = np.unicode_(*args, **kwargs)


# unicode = unicode_


# str_ = unicode_


# str0 = unicode_


# class timedelta64(dolphindb_numpy_generic):
#     def __init__(self, *args, **kwargs):
#         self._np_data = np.timedelta64(*args, **kwargs)

# class uint8(dolphindb_numpy_generic):
#     def __init__(self, *args, **kwargs):
#         self._np_data = np.uint8(*args, **kwargs)


# ubyte = uint8


# class uintp(dolphindb_numpy_generic):
#     def __init__(self, *args, **kwargs):
#         self._np_data = np.uintp(*args, **kwargs)


# uint64 = uintp


# uint0 = uintp


# uint = uintp


# class ushort(dolphindb_numpy_generic):
#     def __init__(self, *args, **kwargs):
#         self._np_data = np.ushort(*args, **kwargs)


# uint16 = ushort


# class uintc(dolphindb_numpy_generic):
#     def __init__(self, *args, **kwargs):
#         self._np_data = np.uintc(*args, **kwargs)


# uint32 = uintc


# class ulonglong(dolphindb_numpy_generic):
#     def __init__(self, *args, **kwargs):
#         self._np_data = np.ulonglong(*args, **kwargs)

