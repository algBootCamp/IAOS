from pandas import Series

##
#@if english
#Columns of a DolphinDB table
#@endif
class Vector(object):
    ##
    #@if english
    #Constructor
    #@param[in] name: specifies the name of the Vector
    #@param[in] data: data (list or series)
    #@param[in] s: connected session object
    #@param[in] tableName: the table name
    #@endif
    def __init__(self, name=None, data=None, s=None, tableName=None):
        self.__name = name
        self.__tableName = tableName
        self.__session = s  # type : session
        if isinstance(data, list):
            self.__vec = Series(data)
        elif isinstance(data, Series):
            self.__vec = data
        else:
            self.__vec = None

    def name(self):
        return self.__name

    def tableName(self):
        return self.__tableName

    def as_series(self, useCache=False):
        if useCache is True and self.__vec is not None:
            return self.__vec
        self.__vec = Series(self.__session.run('.'.join((self.__tableName, self.__name))))
        return self.__vec

    def __str__(self):
        return self.__name

    def __lt__(self, other):
        return FilterCond(self.__name, '<', str(other))

    def __le__(self, other):
        return FilterCond(self.__name, '<=', str(other))

    def __gt__(self, other):
        return FilterCond(self.__name, '>', str(other))

    def __ge__(self, other):
        return FilterCond(self.__name, '>=', str(other))

    def __eq__(self, other):
        return FilterCond(self.__name, '==', str(other))

    def __ne__(self, other):
        return FilterCond(self.__name, '!=', str(other))

    def __add__(self, other):
        return FilterCond(self.__name, '+', str(other))

    def __sub__(self, other):
        return FilterCond(self.__name, '-', str(other))

    def __mul__(self, other):
        return FilterCond(self.__name, '*', str(other))

    def __div__(self, other):
        return FilterCond(self.__name, '/', str(other))

    def __mod__(self, other):
        return FilterCond(self.__name, '%', str(other))

    def __lshift__(self, other):
        return FilterCond(self.__name, '<<', str(other))

    def __rshift__(self, other):
        return FilterCond(self.__name, '>>', str(other))

    def __floordiv__(self, other):
        return FilterCond('int(', str(self), ')')

##
#@if english
#Filtering conditions
#@endif
class FilterCond(object):
    def __init__(self, lhs, op, rhs):
        self.__lhs = lhs
        self.__op = op
        self.__rhs = rhs

    def __str__(self):
        return '(' + str(self.__lhs) + ' ' + str(self.__op) + ' ' + str(self.__rhs) + ')'

    def __or__(self, other):
        return FilterCond(str(self), 'or', str(other))

    def __and__(self, other):
        return FilterCond(str(self), 'and', str(other))

    def __lt__(self, other):
        return FilterCond(str(self), '<', str(other))

    def __le__(self, other):
        return FilterCond(str(self), '<=', str(other))

    def __gt__(self, other):
        return FilterCond(str(self), '>', str(other))

    def __ge__(self, other):
        return FilterCond(str(self), '>=', str(other))

    def __eq__(self, other):
        return FilterCond(str(self), '==', str(other))

    def __ne__(self, other):
        return FilterCond(str(self), '!=', str(other))

    def __add__(self, other):
        return FilterCond(str(self), '+', str(other))

    def __sub__(self, other):
        return FilterCond(str(self), '-', str(other))

    def __mul__(self, other):
        return FilterCond(str(self), '*', str(other))

    def __div__(self, other):
        return FilterCond(str(self), '/', str(other))

    def __mod__(self, other):
        return FilterCond(str(self), '%', str(other))

    def __lshift__(self, other):
        return FilterCond(str(self), '<<', str(other))

    def __rshift__(self, other):
        return FilterCond(str(self), '>>', str(other))

    def __floordiv__(self, other):
        return FilterCond('int(', str(self), ')')
