# -*- coding: utf-8 -*-
__author__ = 'carl'

import uuid


def get_mac_address():
    """
    获取mac地址
    """
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])
