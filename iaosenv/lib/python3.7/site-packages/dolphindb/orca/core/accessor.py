

class CachedAccessor(object):
    """
    Custom property-like object (descriptor) for caching accessors.
    Orca objects are converted to pandas objects using accessor.

    Parameters
    ----------
    name : str
        The namespace this will be accessed under, e.g. ``df.foo``
    accessor : cls
        The class with the extension methods. The class' __init__ method
        should expect one of a ``Series``, ``DataFrame`` or ``Index`` as
        the single argument ``data``
    """
    def __init__(self, name, accessor):
        self._name = name
        self._accessor = accessor

    def __get__(self, obj, cls):
        if obj is None:
            return self._accessor
        obj = obj.to_pandas()
        accessor_obj = self._accessor(obj)
        object.__setattr__(obj, self._name, accessor_obj)
        return accessor_obj