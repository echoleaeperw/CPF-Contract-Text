import time, re
import logging
import base64
from functools import wraps
logger = logging.getLogger(__name__)


def base64_to_encode(bs64_img: str) -> bytes:
    """
    # 解码前端传过来的base64加密图片
    """
    return base64.b64decode(bs64_img.encode('utf8'))  # 解码前端传过来的base64加密图片


def nc_time(func):
    @wraps(func)
    def wapper(*args, **kwargs):
        start = time.monotonic_ns()
        result = func(*args, **kwargs)
        end = time.monotonic_ns()
        logger.info(f"{func.__name__}:用时：{(end - start) / 1000000000}秒")
        return result

    return wapper


def str_to_number(raw_str: str):
    """
    拿到字符串里所有的数字+小数点

    字符串转数字用
    :return:
    """
    num_list = []
    # 遍历每一个字符，只保留数据和小数点，
    for s in raw_str:
        if s.isdigit():
            num_list.append(s)
        else:
            if s == '.':
                num_list.append(s)
    return ''.join(num_list)


def is_number(string):
    """
    判断是否是数字
    """
    pattern = re.compile(r'^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$')
    return bool(pattern.match(string))


if __name__ == '__main__':
    n = str_to_number('$9,921,662.23美元')
    print(n)
