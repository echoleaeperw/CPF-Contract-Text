"""
数据库存连接池
"""

import cx_Oracle
from dbutils.pooled_db import PooledDB
import logging

logger = logging.getLogger(__name__)

# TODO LINUX
# oracle dll文件的位置
lib_dir = r"D:\program\plsq11\instantclient_19_11"
cx_Oracle.init_oracle_client(lib_dir=lib_dir)


class OracleDBPool:
    def __init__(self, host, port, service_name, user, password):
        self.host = host
        self.port = port
        self.service_name = service_name
        self.user = user
        self.password = password

        try:
            self.__dsn = cx_Oracle.makedsn(self.host, self.port, service_name=self.service_name)
            self.pool = PooledDB(cx_Oracle,  # 数据库类型
                                 maxconnections=10,
                                 mincached=2,  # 最大空闲数
                                 blocking=True,  # 默认False，即达到最大连接数时，再取新连接将会报错，True，达到最大连接数时，新连接阻塞，等待连接数减少再连接
                                 user=self.user,
                                 password=self.password,
                                 dsn=self.__dsn,
                                 )
        except Exception as e:
            logger.error('数据池连接异常！', e)
            raise Exception('数据池连接异常!')
        else:
            logger.info('数据池连接成功！')

    def __new__(cls, *args, **kwargs):
        """
        # 利用__new__来启用单例模式
        # 在类的__new__方法中先判断是不是存在实例,如果存在实例,就直接返回,如果不存在实例就创建
        :param args:
        :param kwargs:
        :return:
        """
        if not hasattr(cls, '_instance'):
            OracleDBPool._instance = super().__new__(cls)
        return OracleDBPool._instance

    def get_conn(self):
        """
        以后每次需要数据库连接就调用此方法
        :return:
        """
        conn = self.pool.connection()  #
        return conn


if __name__ == '__main__':
    pass
