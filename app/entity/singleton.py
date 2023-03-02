# -*- coding: utf-8 -*-
__author__ = 'carl'

'''
单例模版 
'''


# noinspection PyMethodParameters
class IaosType(type):

    def __init__(self, name, bases, attrs):
        super(IaosType, self).__init__(name, bases, attrs)
        self.instance = None

    def __call__(self, *args, **kwargs):
        # 1.判断下是否已有对象
        if not self.instance:
            self.instance = self.__new__(self)
        self.__init__(self.instance, *args, **kwargs)
        return self.instance


class Singleton(object, metaclass=IaosType):
    pass

