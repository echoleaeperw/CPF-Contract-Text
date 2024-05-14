from db.DBPoolBase import OracleDBPool
import logging
from app_tools import settings

logger = logging.getLogger(__name__)


class OracleDB:

    def __init__(self, dbm=None):
        if not dbm:
            try:
                dbm = settings.ORACLE
            except AttributeError as e:
                logger.error('数据库连接信息未配置！请先配置')
                logging.error(e)
                raise Exception('数据库连接信息未配置！请先配置')
        try:

            self.db_handler = OracleDBPool(**dbm)
        except Exception as e:
            logger.error('数据库连接异常！')
            logging.error(e)
            raise Exception('数据库连接异常!')
        else:
            logger.info('数据库连接成功接上！')

    def __connect__(self):
        '''
        启动连接
        :return:
        '''
        pool_conn = self.db_handler.get_conn()
        cursor = pool_conn.cursor()
        return pool_conn, cursor

    def __close__(self, conn, cursor):
        """
        关闭连接
        :param conn:
        :param cursor:
        :return:
        """
        cursor.close()
        conn.close()

    def exe_one_execute__(self, sql, args={}):
        """
        单条执行类操作
        :param sql:
        :param args:
        :return:
        """
        conn, cursor = self.__connect__()
        logger.info('具体的sql和args如下')
        logger.info(sql)
        logger.info(args)
        try:
            cursor.execute(sql, args)
            conn.commit()
            logger.info('执行完成')
        except Exception as e:
            # 发生错误时回滚
            conn.rollback()
            logger.info("{s}--sql执行时发生错误，已回滚，请注意！！！".format(s=sql))
            logger.info(e)
            raise Exception('sql执行时发生错误，已回滚，请注意')
        self.__close__(conn, cursor)

    def exe_many_execute__(self, sql, args):
        """
        多条执行类操作
        :param sql:
        :param args:
        :return:
        """
        conn, cursor = self.__connect__()
        logger.info('具体的sql和args如下')
        logger.info(sql)
        logger.info(args)
        try:
            cursor.executemany(sql, args)
            conn.commit()
            logger.info('执行完成')
        except Exception as e:
            # 发生错误时回滚
            conn.rollback()
            logger.error("{s}--sql执行时发生错误，已回滚，请注意！！！".format(s=sql))
            logger.error(e)
            raise Exception('sql执行时发生错误，已回滚，请注意')
        self.__close__(conn, cursor)

    def select_execute__(self, sql):
        conn, cursor = self.__connect__()
        logger.info('具体的sql和args如下')
        logger.info(sql)
        cursor.execute(sql)
        result = cursor.fetchall()
        self.__close__(conn, cursor)
        return result

    def select_title_execute__(self, sql, args_list=None):
        # arg_list 需要是一个list
        conn, cursor = self.__connect__()
        logger.info('具体的sql和args如下')
        logger.info(sql)
        logger.info(args)
        if args_list:
            res = cursor.execute(sql, args_list)
        else:
            res = cursor.execute(sql)
        result = cursor.fetchall()
        title = [i[0] for i in res.description]
        self.__close__(conn, cursor)
        return result, title


if __name__ == '__main__':
    from datetime import datetime
    import json

    js = {"contract_json": [{"ind": 1, "key": "付款单号", "value": "Fk2131230009911"},
                            {"ind": 2, "key": "合同编号", "value": "Y201-123-012-001"},
                            {"ind": 3, "key": "合同金额", "value": "46388212.92"},
                            {"ind": 4, "key": "甲方", "value": "辽河石油勘探局有限公司"},
                            {"ind": 5, "key": "乙方", "value": "中国石油天然气股份有限公司润滑油分公司"}]}
    # 注:结尾不能有分号
    in_sql = """
    insert into IMS_CONTRACT_INFO(ID, REFNO, CONTRACTCODE, MAMOUNT, DTINPUT, DTMODIFY, MESSAGEBODY) values(SEQ_IMS_CONTRACT_INFO.nextval, :REFNO, :CONTRACTCODE, :MAMOUNT, :DTINPUT, :DTMODIFY,:MESSAGEBODY) 
    """

    args = {
        'REFNO': 'Fk0123998111100003',
        'CONTRACTCODE': 'Y201-0921-004',
        'MAMOUNT': 59380.04,
        'DTINPUT': datetime.now(),
        'DTMODIFY': datetime.now(),
        'MESSAGEBODY': json.dumps(js, ensure_ascii=False)
    }

    db = OracleDB()
    # sss = db.exe_one_execute__(in_sql, args)
    sql = 'select * from IMS_CONTRACT_INFO where id = 14'
    data = db.select_title_execute__(sql)
    # json.load(data[0][0][6])  加载json时,需要按文件的方式来加载
    print(json.load(data[0][0][6]))
