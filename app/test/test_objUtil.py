from unittest import TestCase

from entity.base_security import BaseSecurity
from util.objUtil import obj_json


class TestObjUtil(TestCase):
    def test_obj_json(self):
        stk = BaseSecurity()
        stk.stk_id = "123"
        stk.name = "fsadf"
        s = obj_json(stk)
        print(s)
