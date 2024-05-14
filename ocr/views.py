import logging

from fastapi import APIRouter
import pydantic

from app_tools.common import base64_to_encode
from ocr.ocr import paddle_ocr

logger = logging.getLogger(__name__)
ocr_router = APIRouter()


class Image(pydantic.BaseModel):
    image_name: str
    image_b64_file: str


class OcrReq(pydantic.BaseModel):
    image_name: str
    image_result: list[list]


@ocr_router.post('/ocr/prediction', response_model=OcrReq)
def image_ocr(image: Image):
    """
        ## 传入：
        - image_name: str 图片名称
        - image_b64_file: str  base64编码后的图片字符串

        ## 返回：
        - image_name: str  图片名称
        - image_result: 识别结果
        ```python
        # 识别结果格式
        [
            [[['左上角(x,y)'], ['右上角(x,y)'], ['右下角(x,y)'], ['左下角(x,y)']], ['识别结果', '置信度']],
            [[['左上角(x,y)'], ['右上角(x,y)'], ['右下角(x,y)'], ['左下角(x,y)']], ['识别结果', '置信度']],
            [[['左上角(x,y)'], ['右上角(x,y)'], ['右下角(x,y)'], ['左下角(x,y)']], ['识别结果', '置信度']],
            [[['左上角(x,y)'], ['右上角(x,y)'], ['右下角(x,y)'], ['左下角(x,y)']], ['识别结果', '置信度']],
            ...
        ]
        ```
    """
    logger.info(f"image:{image.image_name}")
    data = base64_to_encode(image.image_b64_file)
    image_result, image_name = paddle_ocr(image_file=data, image_name=image.image_name)
    return {'image_name': image_name, 'image_result': image_result}
