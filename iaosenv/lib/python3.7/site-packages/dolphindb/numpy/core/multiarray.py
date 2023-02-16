import numpy
for k in ("getbuffer", "newbuffer", "digitize"):
    try:
        numpy.core.multiarray.__all__.remove(k)
    except:
        pass

from numpy.core.multiarray import *
