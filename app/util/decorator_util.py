# # -*- coding: utf-8 -*-
# __author__ = 'carl'
#
# import functools
#
# def log(func):
#     @functools.wraps(func)
#     def wrapper(*args, **kw):
#         print('call %s():' % func.__name__)
#         return func(*args, **kw)
#     return wrapper
# def blueprintlog(log):
#     """log blueprint decorator"""
#     def decorator(func):
#         @functools.wraps(func)
#         def wrapper(*args, **kw):
#             log.info("访问 %s 接口." % func.__name__)
#             return func(*args, **kw)
#         return wrapper
#     return decorator
