# -*- coding: utf-8 -*-
__author__ = 'carl'

import json


def obj_json(obj):
    """实体类转dict"""
    obj_dict = obj.__dict__
    spl_str = "_" + str(obj.__class__).split('.')[-1][:-2] + "__"
    target_dict = dict()
    for k, v in obj_dict.items():
        target_dict[k.replace(spl_str, '')] = v
    # json_str = json.dumps(obj=target_dict, default=lambda x: x.__dict__, sort_keys=False, indent=2)
    json_str = json.dumps(obj=target_dict)
    return json_str
