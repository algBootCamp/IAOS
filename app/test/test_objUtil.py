from unittest import TestCase

from entity.base_security import BaseSecurity
from util.obj_util import obj_dict


class TestObjUtil(TestCase):
    def test_obj_json(self):
        stk = BaseSecurity()
        stk.stk_id = "123"
        stk.name = "fsadf"
        s = obj_dict(stk)
        print(s)
