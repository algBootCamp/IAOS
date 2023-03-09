# -*- coding: utf-8 -*-
__author__ = 'carl'

import pickle


# noinspection PyShadowingNames
def obj_dict(obj):
    """实体类转dict"""
    obj_dict = obj.__dict__
    spl_str = "_" + str(obj.__class__).split('.')[-1][:-2] + "__"
    target_dict = dict()
    for k, v in obj_dict.items():
        target_dict[k.replace(spl_str, '')] = v
    # json_str = json.dumps(obj=target_dict, default=lambda x: x.__dict__, sort_keys=False, indent=2)
    # json_str = json.dumps(obj=target_dict)
    return target_dict


def method_call(obj, method_name, args):
    """调用任意对象中的任意函数"""
    if hasattr(obj, method_name):
        return getattr(obj, method_name)(args)
    else:
        raise ModuleNotFoundError("{} has no attr {}".format(obj, method_name))


def dumps_data(df):
    """
    data序列化
    """
    try:
        # print("df:", df)
        content = pickle.dumps(df)
        return content
    except Exception as e:
        raise e


def loads_data(content):
    """
    data反序列化
    """
    try:
        origin_data = pickle.loads(content)
        return origin_data
    except Exception as e:
        raise e
