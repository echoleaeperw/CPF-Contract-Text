"""
处理文件
可以将PDF转化为文件
"""
import json
import os

from pdf2image import convert_from_path
import fitz


def pdf_to_image(pdf_path):
    images = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            img = page.get_pixmap(get_pixmap=False)
            images.append(img)
    return images


def extract_pdf_images(pdf_path, output_folder):
    try:
        if not os.path.exists(output_folder):
            # 如果该文件夹不存在，则创建新文件夹
            os.makedirs(output_folder)
        # 从PDF中提取图像
        images = pdf_to_image(pdf_path)
        # 逐页保存图像为JPG文件
        for i, image in enumerate(images):
            path = f"{output_folder}/{i + 1}.jpg"
            image.save(path)
    except Exception as e:
        raise e


# 允许上传的文件格式
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'bmp', 'png', 'jpeg', 'rgb', 'tif', 'tiff', 'gif'}


# 检查上传的文件格式是否合法
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_json_data(data, filename, path='.'):
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, filename), 'w', encoding='utf-8') as f:
        data['data'] = [{k: v for k, v in item.items() if k != 'page'} for item in data['data']]
        json.dump(data, f, ensure_ascii=False, indent=4, skipkeys=lambda x: x == 'page')
