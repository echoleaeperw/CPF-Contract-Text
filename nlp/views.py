import logging

from fastapi import APIRouter
import pydantic

from app_tools.common import base64_to_encode
from ocr.ocr import paddle_ocr
from nlp.match import match_keyword, ocr_to_text, nlp_result_to_list

logger = logging.getLogger(__name__)
nlp_router = APIRouter()


class NLPText(pydantic.BaseModel):
    text_id: str
    text: str
    keywords: list[str]


class NLPTextReq(pydantic.BaseModel):
    text_id: str
    text_result: list


@nlp_router.post('/nlp/prediction', response_model=NLPTextReq)
def text_nlp(text: NLPText):
    """
        ## 传入：
        - text_id: str 文本标识
        - text: str  文本内容
        - keywords: list 抽取关系的关键字参数

        ## 返回：
        - text_id: str 文本标识
        - text_result: list 关系结果
        ```python
        # 关系结果格式
            [{'甲方': [{'text': '三亚市崖州区国有资产管理', 'start': 129, 'end': 141, 'probability': 0.9164909148587697}],
                   '乙方': [{'text': '海南神铨汽车销售有限公司(签章)开发有限责任公司', 'start': 145, 'end': 170,
                           'probability': 0.5705488173078592}], '开户行': [
            {'text': '中国建设银行股份有限公司海口海秀路支行', 'start': 240, 'end': 260, 'probability': 0.8204746396851554}],
                   '签订日期': [{'text': '7017. 9. 6', 'start': 353, 'end': 363, 'probability': 0.8123617228616666}]}]
    :param text:
    :return:
    """
    text_list = match_keyword(text.text, text.keywords)
    return {'text_id': text.text_id, 'text_result': text_list}


class CompositeNLP(pydantic.BaseModel):
    image_name: str
    image_b64_file: str
    keywords: list[str]


class CompositeReq(pydantic.BaseModel):
    image_name: str
    image_result: list[dict]


@nlp_router.post('/composite/prediction', response_model=CompositeReq)
def ocr_to_nlp(image: CompositeNLP):
    """
        ## 传入：
        - image_name: str 图片名称
        - image_b64_file: str  base64编码后的图片字符串
        - keywords: list

        ## 返回：
        - image_name: str  图片名称
        - image_result: list[dict]关系结果
        ```python
        # 关系结果格式
            {
                "image_name": "123.jpg",
                "image_result": [
                    {
                        "关键字1": [
                            {
                                "text": "对应的文本内容",
                                "probability": 0.9164909725475567,
                                "position": [[453, 1103], [1206, 1188]]
                            }
                        ],
                        "关键字2": [
                            {
                                "text": "对应的文本内容",
                                "probability": 0.9164909725475567,
                                "position": [[453, 1103], [1206, 1188]]
                            }
                        ],
                        ...
                    }
                ]
            }
        ```
    """
    logger.info(f"image:{image.image_name}")
    data = base64_to_encode(image.image_b64_file)  # 解码b64的图片
    ocr_result = paddle_ocr(image_file=data, image_name=image.image_name)  # 识别
    text = ocr_to_text(ocr_result[0])
    nlp_result = match_keyword(text, image.keywords)  # 关系抽取
    text_list = nlp_result_to_list(ocr_result=ocr_result[0], nlp_result=nlp_result)  # 匹配文件对应的位置
    return {'image_name': image.image_name, 'image_result': text_list}
