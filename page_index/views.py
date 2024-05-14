import logging, os, uuid, time, base64, json
from datetime import datetime
import pydantic

from fastapi import APIRouter, Request, UploadFile, HTTPException
from fastapi.templating import Jinja2Templates

from .logo import logostr
from .file_handle import allowed_file, save_json_data
from .contract_identification import identification_pdf, identification_img, dedupe_by_first_two_positions, \
    get_coordinate
from db.oracle import OracleDB
from app_tools.common import is_number
from app_tools.settings import UPLOAD_PATH

logger = logging.getLogger(__name__)
page_index_router = APIRouter()


@page_index_router.get('/')
def image_ocr(request: Request):
    """
        用户操作的页面
    """
    templates = Jinja2Templates(directory="templates")
    return templates.TemplateResponse(
        'main.html',
        {
            'request': request,  # 注意，返回模板响应时，必须有request键值对，且值为Request请求对象
            'word': 'Hello World'
        }
    )


@page_index_router.get('/get_logo')
def get_logo():
    return logostr


def get_file_path():
    """
    根据日期和UUID生成文件的存储路径
    # eg. 2023_08_24/01a054a1-992b-428b-9244-bd45ab07cbfe/image
    """
    # 获取当前时间
    now = datetime.now()
    # 将时间格式化为指定的格式
    formatted_date = now.strftime('%Y_%m_%d')
    # 生成一个随机的UUID
    random_uuid = uuid.uuid4()
    # 将UUID转换为字符串
    uuid_string = str(random_uuid)
    filepath_path = f"{UPLOAD_PATH}/{formatted_date}/{uuid_string}/image"
    return filepath_path


def is_file_format_validity(files: list[UploadFile]):
    # 先判断文件格式是否符合要求,只要有一个不符合要求就返回失败
    for file in files:
        if not allowed_file(file.filename):
            logger.info(f'{file.filename}:文件格式不正确！！！')
            raise HTTPException(status_code=422, detail=f'{file.filename}:文件格式不正确')


def file_storage_name(index: int, file_name: str) -> str:
    """
    返回存储时的新文件名称。
    新名称格式：前缀+序号+后缀
    """
    file_name_prefix = file_name.rsplit('.', 1)[0]  # 文件名称的前缀
    file_name_postfix = file_name.rsplit('.', 1)[-1]  # 文件名称的后缀
    filename = f"{file_name_prefix}{index}.{file_name_postfix}"
    return filename


def file_storage(files: list[UploadFile], filepath_sub: str) -> None:
    """
    存储上传的文件
    """
    for file in files:
        if not os.path.exists(filepath_sub):
            # 如果该文件夹不存在，则创建新文件夹
            os.makedirs(filepath_sub)
        filepath = os.path.join(filepath_sub, file.filename)
        logger.info(f'开始保存文件:{filepath}')
        with open(filepath, 'wb') as f:
            f.write(file.file.read())
        logger.info(f'保存文件成功：{filepath}')


# 文件上传接口
@page_index_router.post('/upload')
def upload_files(file: list[UploadFile]):
    start_time = time.monotonic()
    # 定义响应的结构
    response = {
        "code": 200,
        "message": "success",
        "data": []
    }
    files = file
    # 生成文件的存储路径
    filepath_sub = get_file_path()

    # 先判断文件格式是否符合要求
    is_file_format_validity(files=files)

    # 依次存储上传的所有文件
    file_storage(files=files, filepath_sub=filepath_sub)

    # 批量识别
    for file in files:
        filename = file.filename
        if 'pdf' in filename:
            result = identification_pdf(pdf_path=filepath_sub, filename=filename)
        else:
            result = identification_img(img_path=filepath_sub)

    # 循环遍历字典列表，转换为JSON格式
    if len(result) > 0:

        sorted_tuples_list = sorted(result, key=lambda x: x[0])
        for index, data in enumerate(sorted_tuples_list, start=1):
            filename = file.filename
            if 'pdf' in filename:
                with open(f"{filepath_sub}/{data[3]}.jpg", "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            else:
                with open(f"{filepath_sub}/{data[3]}", "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            item = {
                "key": data[0],
                "value": data[1],
                "confidence": data[2],
                "page": encoded_string,
                "pagenum": data[3],
                "ind": index
            }
            response["data"].append(item)
    save_json_data(response.copy(), 'data.json', path=f"{filepath_sub}")  # .replace('1.pdf', '')
    end_time = time.monotonic()
    logger.info(f"总用时：{end_time - start_time}")
    return response


# 保存
class ContractJson(pydantic.BaseModel):
    contract_json: list


class ContractSaveReq(pydantic.BaseModel):
    status: str
    msg: str
    data: dict


@page_index_router.post('/contract/save', response_model=ContractSaveReq)
def save_contract(contract: ContractJson):
    """
        保存前端发来的合同数据
        - 前台发JSON  注，如果前端要发JSON，发送时的contentType 必须是：'application/json'
        - 付款单号、合同号、合同金额三项必须有
        - 其它字段已JSON的形式直接存入

        状态说明
        status 1 成功 0 失败
    """

    data = contract.contract_json  # 拿到原始数据
    # 1 先对数据清理,并将行数据转为地点
    data_dict = clean_contract_data(data)
    # 2 在对数据做校验
    flag, msg = validate_contract_data(data_dict)
    if flag:
        # 3 最后进行数据保存入库
        flag = save_contract_data(data_dict, data)
        if flag:
            # 保存成功
            status = 1
            msg = '保存成功'
        else:
            status = 0
            msg = '保存失败'
    else:
        status = 0
    response = {
        'status': status,
        'msg': msg,
        'data': {}
    }

    return response


def clean_contract_data(data):
    """
    - 1清理数据,如空格等
    - 2将list转为dict
    """
    # 先根据行顺序ind,对数据进行排序,
    # 后续如果出现重复的key,则value都只取最后一个值
    try:
        data = sorted(data, key=lambda x: int(x['ind']), reverse=False)
    except ValueError as ve:
        logger.info('ind字段存在不是数字的情况')
        raise ValueError('ind字段存在不是数字的情况')
    data_dict = {}
    for i in data:
        # 清空前台的空格
        key = i['key'].strip()
        value = i['value'].strip()
        # 转为字典
        data_dict[key] = value
    return data_dict


def validate_contract_data(data_dict):
    """
    对前台传过来的数据进行校验
    """
    # 1、key或value都不能为空
    if data_dict.get('付款单号', None) and data_dict.get('合同编号', None) and data_dict.get('合同金额', None):
        # 2、合同金额，必须是数字
        if is_number(str(data_dict.get('合同金额', None))):
            flag = True
            msg = '校验通过'
        else:
            flag = False
            msg = '合同金额校验失败：必须是阿拉伯数字+小数点组成的标准数字'
    else:
        flag = False
        msg = '必输项校验失败：付款单号、合同编号、合同金额三项不允许为空'
    return flag, msg


def save_contract_data(data_dict, data):
    """
    将校验及清理过的数据存入库里
    :param data_dict:
    :param data: 原值
    :return:
    """
    flag = True
    # 插入数据的sql，目前没有用到
    in_sql = """
    insert into IMS_CONTRACT_INFO(ID, REFNO, CONTRACTCODE, MAMOUNT, DTINPUT, DTMODIFY, MESSAGEBODY) values(SEQ_IMS_CONTRACT_INFO.nextval, :REFNO, :CONTRACTCODE, :MAMOUNT, :DTINPUT, :DTMODIFY,:MESSAGEBODY)
    """

    # 没有就插入，有则更新
    up_in_sql = """
    MERGE INTO  ims_contract_info c
    USING (select 
     :REFNO as REFNO,
     :CONTRACTCODE as CONTRACTCODE
     FROM dual
     ) d
    on (d.REFNO = c.REFNO and d.CONTRACTCODE = c.CONTRACTCODE)
    when MATCHED  then
    update 
    set MAMOUNT = :MAMOUNT,
    DTMODIFY = :DTMODIFY,
    MESSAGEBODY = :MESSAGEBODY
    when not MATCHED  then
    insert (ID, REFNO, CONTRACTCODE, MAMOUNT, DTINPUT, DTMODIFY, MESSAGEBODY) values(SEQ_IMS_CONTRACT_INFO.nextval, :REFNO, :CONTRACTCODE, :MAMOUNT, :DTINPUT, :DTMODIFY,:MESSAGEBODY)
    """

    args = {
        'REFNO': data_dict['付款单号'],
        'CONTRACTCODE': data_dict['合同编号'],
        'MAMOUNT': data_dict['合同金额'],
        'DTINPUT': datetime.now(),
        'DTMODIFY': datetime.now(),
        'MESSAGEBODY': json.dumps(data, ensure_ascii=False)  # 这里存入的前台的原始值
    }
    logger.info(up_in_sql)
    logger.info(args)
    try:
        db = OracleDB()
        db.exe_one_execute__(up_in_sql, args)
    except Exception as e:
        logger.error('数据插入失败')
        logger.error(e)
        flag = False
    return flag
