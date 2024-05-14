import os

# 拿到当前系统的换行符
new_line = os.linesep  # 不同的系统，不相同

# 项目的根目录
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# linux 中文件存放的目录
BASE_MODEL_DIR = os.path.join(BASE_PATH, 'models')

# UIE_BASE_MODEL_DIR = os.path.join(BASE_MODEL_DIR, 'uie-base')
# DET_MODEL_DIR = os.path.join(BASE_MODEL_DIR, 'ch_PP-OCRv3_det_infer')
# REC_MODEL_DIR = os.path.join(BASE_MODEL_DIR, 'ch_PP-OCRv3_rec_infer')
# CLS_MODEL_DIR = os.path.join(BASE_MODEL_DIR, 'ch_ppocr_mobile_v2.0_cls_infer')

# #  测试时各模型的默认路径位置
UIE_BASE_MODEL_DIR = r'C:\Users\issuser\Desktop\py0602\models\inference\uie-base'
DET_MODEL_DIR = r'C:\Users\issuser\Desktop\py0602\models\inference\ch_PP-OCRv3_det_infer'
REC_MODEL_DIR = r'C:\Users\issuser\Desktop\py0602\models\inference\ch_PP-OCRv3_rec_infer'
CLS_MODEL_DIR = r'C:\Users\issuser\Desktop\py0602\models\inference\ch_ppocr_mobile_v2.0_cls_infer'

# 文件上传到服务器的路径
# windows 测试用
# UPLOAD_PATH = r'C:\Users\issuser\Desktop\AIupload'
# Linux 生产用
UPLOAD_PATH = os.path.join(os.path.dirname(BASE_PATH), 'uploads')

#
"""ERP
ORACLE = {
    'host': '10.211.208.32',
    'port': 1521,
    'service_name': 'testerp32',
    'user': 'testerp32',
    'password': 'dbtesterp32u208'
}
"""
ORACLE = {
    'host': '10.211.208.32',
    'port': 1521,
    'service_name': 'testerp32',
    'user': 'ocr_verif32',
    'password': 'dbocr_verif32u208'
}

if __name__ == '__main__':
    print(BASE_PATH)
