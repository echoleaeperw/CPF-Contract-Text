import os
import logging.config
from app_tools.settings import BASE_PATH


class Logger:
    def __init__(self):
        # 定义三种日志输出格式 开始
        self.standard_format = '[%(asctime) -s][%(threadName)s:%(thread)d][task_id:%(name)s]' \
                               '[%(filename)s:%(lineno)d][%(levelname)s][%(message)s]'
        self.simple_format = '[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d]%(message)s'
        self.id_simple_format = '[%(levelname)s][%(asctime)s] %(message)s'

    def get_log_path(self):
        # 日志文件的位置
        logfile_dir = os.path.join(BASE_PATH, 'logs')

        # 日志文件的名称
        logfile_name = 'app.log'

        # 如果不存在定义的日志目录就创建一个

        if not os.path.isdir(logfile_dir):
            os.mkdir(logfile_dir)

        # log文件的全路径
        logfile_path = os.path.join(logfile_dir, logfile_name)
        return logfile_path

    def get_logging_config(self):
        log_path = self.get_log_path()
        # log配置字典
        LOGGING_DIC = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': self.standard_format,
                    'datefmt': '%Y-%m-%d %H:%M:%S',
                },
                'simple': {
                    'format': self.simple_format
                },

            },
            'filters': {},
            'handlers': {
                'console': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',  # 打印到屏幕
                    'formatter': 'simple'
                },
                'time_logger': {
                    'level': 'DEBUG',
                    'class': 'logging.handlers.TimedRotatingFileHandler',  # 保存到文件。自动切日志
                    'filename': log_path,  # 日志文件
                    'when': 'H',  # 时间单位    # S - Seconds # M - Minutes # H - Hours  # D - Days
                    'interval': 1,  # 时间间隔
                    'backupCount': 36,  # 日志文件备份个数
                    'formatter': 'standard',  # 使用的日志文件格式
                    'encoding': 'utf-8',  # 日志文件的编码，再也不用担心中文log乱码了
                },

            },

            'loggers': {
                '': {
                    'handlers': ['time_logger', 'console'],  # 这里把上面定义的两个handler都加上，即log数据既写入文件又打印到屏幕
                    'level': 'INFO',
                    'propagate': True,  # 向上（更高level的logger）传递
                },
            },
        }
        return LOGGING_DIC

    def getLogger(self, name=None):
        logging.config.dictConfig(self.get_logging_config())  # 导入上面定义的配置
        return logging.getLogger(name)


if __name__ == '__main__':
    logger = Logger().get_logger(__name__)
    logger.info('It works!')  # 记录该日志配置文件的运行状态
    from test import b42_img

    for i in range(1000):
        import time

        # time.sleep(2)
        logger.info(b42_img[:1000])
        # logger.info('It works!')
