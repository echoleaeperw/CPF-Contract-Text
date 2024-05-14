"""
匹配关键字
"""
import logging
from app_tools import common, settings

logger = logging.getLogger(__name__)


@common.nc_time
def match_keyword(key, result, page_num, keywords):
    # 遍历result，匹配关键字
    txts = []
    for line in result:
        txt = line[1][0]
        if isinstance(txt, list):
            txt = ' '.join(txt)
        txts.append(txt)
    all_text = settings.new_line.join(txts)
    schema = []
    for key in keywords:
        for i in keywords[key]:
            schema.append(i)

    from nlp.match import match_keyword
    result = match_keyword(text=all_text, keywords=schema)
    return result
