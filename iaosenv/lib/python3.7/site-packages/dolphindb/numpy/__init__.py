import sys

from . import core
from .core import *
from .core.multiarray import *
from .core.multiarray_umath import *
from . import compat
from . import lib
from .lib import *

from . import linalg
from . import fft
from . import polynomial
from . import random
from . import ctypeslib
from . import ma
from . import matrixlib as _mat
from .matrixlib import *
from .compat import long

if sys.version_info[0] >= 3:
    from builtins import bool, int, float, complex, object, str
    unicode = str
else:
    from __builtin__ import bool, int, float, complex, object, unicode, str
