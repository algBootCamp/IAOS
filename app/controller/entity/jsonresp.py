# -*- coding: utf-8 -*-
__author__ = 'carl'

'''
统一的json返回格式
'''


class JsonResponse(object):
    """
    统一的json返回格式
    """
    CODE_ERROR = '-1'
    CODE_SUCCESS = '0'

    def __init__(self, data, code, msg):
        self.data = data
        self.code = code
        self.msg = msg

    @classmethod
    def success(cls, data=None, code=CODE_SUCCESS, msg='success'):
        return cls(data, code, msg)

    @classmethod
    def error(cls, data=None, code=CODE_ERROR, msg='error'):
        return cls(data, code, msg)

    def to_dict(self):
        return {
            "code": self.code,
            "msg": self.msg,
            "data": self.data
        }
