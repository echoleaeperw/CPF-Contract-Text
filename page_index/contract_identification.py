import glob
import time
from .file_handle import *
from .image import draw_rectangle_paddle
from .match import match_keyword
from ocr.ocr import paddle_ocr
import logging
from datetime import datetime
from app_tools import settings

logger = logging.getLogger(__name__)

keywords = {"买方": ["买方", "甲方"],
            "卖方": ["卖方", "乙方"],
            "总价": ["总价", "价格", "小写", "合同金额"],
            "税率": ["税率"],
            "纳税人识别号": ["纳税人识别号"],
            "开户行": ["开户行"],
            "住所地": ["住所地"],
            "合同自编号": ["合同自编号", '合同编号'],
            "签订日期": ["签订日期"],
            "采购订单号": ["采购订单号"],
            "工程名称": ["工程名称"],
            "法定代表(负责)人": ["法定代表"]}


def identification_pdf(pdf_path, filename):
    # 识别pdf为图片
    output_folder = f"{pdf_path}"
    logger.info(f"pdf2image-start{filename}")
    start_time = time.time()
    extract_pdf_images(pdf_path=f"{pdf_path}/{filename}", output_folder=output_folder)
    end_time = time.time()
    logger.info(f"pdf2image-end{filename}-耗费时间：[{end_time - start_time}]")

    # 获取文件夹中所有图片的路径
    images_path = glob.glob(os.path.join(output_folder, "*.jpg"))
    new_result_list = []
    # 返回结果
    list_ = []
    # 遍历文件夹中所有图片
    for image_path in images_path:
        image_name = os.path.basename(image_path)  # 获取文件名
        result, page_num = paddle_ocr(image_file=image_path, image_name=f"{image_name}".split('.')[0])
        logger.info('OCR识别结果 start'.center(50, '*'))
        logger.info(result)
        logger.info('OCR识别结果 end'.center(50, '*'))
        # 循环匹配关键字
        new_result = match_keyword(key=keywords,
                                   result=result,
                                   page_num=page_num,
                                   keywords=keywords,
                                   )
        logger.info(f'结果开始时间:{datetime.now()}')
        logger.info(f'------------{new_result}')
        if new_result is not None:
            if len(new_result[0]) == 0:
                os.remove(image_path)
                print(f"无关键字：删除文件{image_path}")
            else:
                # 识别结果
                new_result_list.append({"image_path": image_path,
                                        "new_result": new_result,
                                        "result": result,
                                        "page_num": page_num
                                        })

        # 识别结果
    for _r in new_result_list:
        rectangles = []
        for res in _r["new_result"]:
            for value in res:
                for v in res[value]:
                    top_left, bottom_right = get_coordinate(_r["result"], v["text"])
                    if top_left != 0 and bottom_right != 0:
                        rectangles.append((top_left, bottom_right))
                        list_.append((value, v["text"], "{:.2%}".format(eval(f"{v['probability']}")), _r["page_num"]))

        logger.info(f'结果结束时间:{datetime.now()}')
        # 记录开始时间
        start_time = time.time()

        logger.info(f"draw_rectangle_paddle-start-{_r['image_path']}")
        draw_rectangle_paddle(image_path=_r["image_path"], rectangles=rectangles)
        end_time = time.time()
        logger.info(f"draw_rectangle_paddle-end-{_r['image_path']}-耗费时间：[{end_time-start_time}]")
    dict_ = {}
    for tpl in list_:
        key = (tpl[0], tpl[1])
        if key in dict_:
            if eval(f"{dict_[key][2].replace('%', '')} < {tpl[2].replace('%', '')}"):
                dict_[key] = tpl
        else:
            dict_[key] = tpl
    result_list = list(dict_.values())
    return result_list


def dedupe_by_first_two_positions(seq):
    """
    元组去重
    :param seq:
    :return:
    """
    seen = set()
    for tpl in seq:
        key = tpl[0], tpl[1]
        if key not in seen:
            seen.add(key)
            yield tpl


def get_coordinate(result, value):
    """
    获取坐标
    :param result:
    :param value:
    :return:
    """
    for line in result:
        txt = line[1][0]
        if settings.new_line in value:
            value = value.split(settings.new_line)[0]
        if value in txt:
            top_left = (int(eval(f"{line[0][0][0]}")),
                        int(eval(f"{line[0][0][1]}")))
            bottom_right = (int(eval(f"{line[0][2][0]}")),
                            int(eval(f"{line[0][2][1]}")))
            res = (top_left, bottom_right)
            return res
    return (0, 0)


def identification_img(img_path):
    """

    result = [('甲方', '三亚市崖州区国有资产管理', '91.65%', '30114645z7cj'),
          ('乙方', '海南神铨汽车销售有限公司(签章)\n开发有限责任公司', '57.05%', '30114645z7cj'),
          ('开户行', '中国建设银行股份有限公司\n海口海秀路支行', '82.05%', '30114645z7cj'),
          ('签订日期', '7017. 9. 6', '81.24%', '30114645z7cj')]
    """
    # 获取文件夹中所有图片的路径
    images_path = glob.glob(os.path.join(img_path, "*.jpg"))
    images_path.extend(glob.glob(os.path.join(img_path, "*.bmp")))
    images_path.extend(glob.glob(os.path.join(img_path, "*.png")))
    images_path.extend(glob.glob(os.path.join(img_path, "*.jpeg")))
    images_path.extend(glob.glob(os.path.join(img_path, "*.rgb")))
    images_path.extend(glob.glob(os.path.join(img_path, "*.tif")))
    images_path.extend(glob.glob(os.path.join(img_path, "*.tiff")))
    images_path.extend(glob.glob(os.path.join(img_path, "*.gif")))

    # 返回结果
    list_ = []

    # 遍历文件夹中所有图片
    for image_path in images_path:
        image_name = os.path.basename(image_path)  # 获取文件名
        result, page_num = paddle_ocr(image_file=image_path, image_name=f"{image_name}")
        logger.info('%' * 50)
        logger.info(page_num)
        logger.info('%' * 50)
        # 循环匹配关键字
        new_result = match_keyword(key=keywords,
                                   result=result,
                                   page_num=page_num,
                                   keywords=keywords)

        if new_result is not None:
            # 识别结果
            for res in new_result:
                for value in res:
                    for v in res[value]:
                        coo = get_coordinate(result, v["text"])
                        if coo is not None:
                            rectangles = [(coo[0], coo[1])]
                            draw_rectangle_paddle(image_path=image_path, rectangles=rectangles)
                            # 原值,内容，置信度，文件名称
                        list_.append((value, v["text"], "{:.2%}".format(eval(f"{v['probability']}")), page_num))
    dict_ = {}
    for tpl in list_:
        key = (tpl[0], tpl[1])
        if key in dict_:
            if dict_[key][2] < tpl[2]:
                dict_[key] = tpl
        else:
            dict_[key] = tpl
    result_list = list(dict_.values())
    return result_list
