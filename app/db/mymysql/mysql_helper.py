# -*- coding: utf-8 -*-
__author__ = 'carl'

import logging

from db.mymysql.mysql_db_pool import get_my_connection

'''
mysql操作：增删改查
执行语句查询： 有结果返回结果，没有返回0；
增/删/改   返回变更数据的数量，没有返回0

使用方法：
     db = MySqLHelper()
     sql1 = 'select * from tableX where xx=%s'
     args = 'python'
     ret = db.selectone(sql=sql1, param=args)
'''
log = logging.getLogger("app")
log_err = logging.getLogger("log_err")


# noinspection DuplicatedCode,PyBroadException
class MySqLHelper(object):

    def __new__(cls, *args, **kwargs):
        """保证单例"""
        if not hasattr(cls, 'inst'):
            cls.inst = super(MySqLHelper, cls).__new__(cls, *args, **kwargs)
        return cls.inst

    def __init__(self):
        """从数据池中获取连接"""
        self.db = get_my_connection()

    def execute(self, sql, param=None, autoclose=False):
        """
         封装执行命令
        【主要判断是否有参数和是否执行完就释放连接】
        :param sql: 字符串类型，sql语句
        :param param: sql语句中要替换的参数"select %s from tab where id=%s" 其中的%s就是参数
        :param autoclose: 是否关闭连接
        :return: 返回连接conn和游标cursor
        """
        cursor, conn = self.db.getconn()
        count = 0
        log.info("start execute sql: %s" % sql)
        try:
            if param:
                count = cursor.execute(sql, param)
            else:
                count = cursor.execute(sql)
            conn.commit()
            if autoclose:
                self.close(cursor, conn)
        except Exception as e:
            log_err.error("execute sql exception", e)
        return cursor, conn, count

    def close(self, cursor, conn):
        """释放连接归还给连接池"""
        cursor.close()
        conn.close()

    def selectall(self, sql, param=None):
        """查询所有"""
        cursor = None
        conn = None
        count = None
        try:
            cursor, conn, count = self.execute(sql, param)
            res = cursor.fetchall()
            return res
        except Exception as e:
            log_err.error("selectall exception", e)
            return count
        finally:
            self.close(cursor, conn)

    def selectone(self, sql, param=None):
        """查询单条"""
        cursor = None
        conn = None
        count = None
        try:
            cursor, conn, count = self.execute(sql, param)
            res = cursor.fetchone()
            return res
        except Exception as e:
            log_err.error("selectall exception", e)
            return count
        finally:
            self.close(cursor, conn)

    def insertone(self, sql, param):
        """新增单条数据"""
        cursor = None
        conn = None
        count = None
        try:
            cursor, conn, count = self.execute(sql, param)
            # 获取当前插入数据的主键id，该id应该为自动生成为好
            # _id = cursor.lastrowid()
            conn.commit()
            return count
        except Exception as e:
            log_err.error("insertone exception", e)
            conn.rollback()
            return count
        finally:
            self.close(cursor, conn)

    def insertmany(self, sql, param):
        """
        新增多条数据
        :param sql:
        :param param: 必须是元组或列表[(),()]或（（），（））
        :return:
        """
        cursor, conn, count = self.db.getconn()
        try:
            cursor.executemany(sql, param)
            conn.commit()
            return count
        except Exception as e:
            log_err.error("insertmany exception", e)
            conn.rollback()
            return count
        finally:
            self.close(cursor, conn)

    def delete(self, sql, param=None):
        """删除"""
        cursor = None
        conn = None
        count = None
        try:
            cursor, conn, count = self.execute(sql, param)
            return count
        except Exception as e:
            log_err.error("delete exception", e)
            conn.rollback()
            return count
        finally:
            self.close(cursor, conn)

    def update(self, sql, param=None):
        """更新"""
        cursor = None
        conn = None
        count = None
        try:
            cursor, conn, count = self.execute(sql, param)
            conn.commit()
            return count
        except Exception as e:
            log_err.error("update exception", e)
            conn.rollback()
            return count
        finally:
            self.close(cursor, conn)


if __name__ == '__main__':
    db = MySqLHelper()

    # TODO 查询单条
    # sql1 = 'select * from userinfo where name=%s'
    # args = 'python'
    # ret = db.selectone(sql=sql1, param=args)
    # print(ret)  # (None, b'python', b'123456', b'0')

    # TODO 增加单条
    # sql2 = 'insert into hotel_urls(cname,hname,cid,hid,url) values(%s,%s,%s,%s,%s)'
    # ret = db.insertone(sql2, ('1', '2', '1', '2', '2'))
    # print(ret)

    # TODO 增加多条
    # sql3 = 'insert into userinfo (name,password) VALUES (%s,%s)'
    # li = li = [
    #     ('分省', '123'),
    #     ('到达','456')
    # ]
    # ret = db.insertmany(sql3,li)
    # print(ret)

    # TODO 删除
    # sql4 = 'delete from  userinfo WHERE name=%s'
    # args = 'xxxx'
    # ret = db.delete(sql4, args)
    # print(ret)

    # TODO 更新
    # sql5 = r'update userinfo set password=%s WHERE name LIKE %s'
    # args = ('993333993', '%old%')
    # ret = db.update(sql5, args)
    # print(ret)
