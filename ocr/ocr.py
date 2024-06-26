"""
OCR
"""
from paddleocr import PaddleOCR
import logging
from app_tools import common, settings

logger = logging.getLogger(__name__)


@common.nc_time
def paddle_ocr(image_file: bytes, image_name: str):
    """
    image_file : 路径和文件都可以
    result = [
        [[['左上角(x,y)'], ['右上角(x,y)'], ['右下角(x,y)'], ['左下角(x,y)']], ('识别结果', '置信度')],
        [[['左上角(x,y)'], ['右上角(x,y)'], ['右下角(x,y)'], ['左下角(x,y)']], ('识别结果', '置信度')],
        [[['左上角(x,y)'], ['右上角(x,y)'], ['右下角(x,y)'], ['左下角(x,y)']], ('识别结果', '置信度')],
        [[['左上角(x,y)'], ['右上角(x,y)'], ['右下角(x,y)'], ['左下角(x,y)']], ('识别结果', '置信度')],
        ...
    ]
    """
    try:
        ocr = PaddleOCR(use_angle_cls=True,
                        lang="ch",  # ch 中文
                        det_model_dir=settings.DET_MODEL_DIR,
                        rec_model_dir=settings.REC_MODEL_DIR,
                        cls_model_dir=settings.CLS_MODEL_DIR,
                        enable_mkldnn=True,
                        cpu_threads=4,
                        zero_copy_run=True,
                        cls_batch_num=10,  # 进行分类时，同时前向的图片数
                        max_batch_size=20,
                        rec_batch_num=10,
                        )
        result = ocr.ocr(image_file, cls=True)
        if len(result) > 0:
            return result[0], image_name
        else:
            logger.error('OCR识别错误，无法提取结果')
            raise Exception(f"Error:OCR识别错误，无法提取结果")
    except Exception as e:
        logger.error(f"ocr识别错误{e}")
        raise Exception(f"Error:ocr识别错误{e}")


if __name__ == '__main__':
    a = dict(help='==SUPPRESS==', use_gpu=False, use_xpu=False, use_npu=False, ir_optim=True, use_tensorrt=False,
             min_subgraph_size=15, precision='fp32', gpu_mem=500, image_dir=None, page_num=0, det_algorithm='DB',
             det_model_dir='/root/.paddleocr/whl/det/ch/ch_PP-OCRv3_det_infer', det_limit_side_len=960,
             det_limit_type='max', det_box_type='quad', det_db_thresh=0.3, det_db_box_thresh=0.6,
             det_db_unclip_ratio=1.5, max_batch_size=10, use_dilation=False, det_db_score_mode='fast',
             det_east_score_thresh=0.8, det_east_cover_thresh=0.1, det_east_nms_thresh=0.2,
             det_sast_score_thresh=0.5, det_sast_nms_thresh=0.2, det_pse_thresh=0, det_pse_box_thresh=0.85,
             det_pse_min_area=16, det_pse_scale=1, scales=[8, 16, 32], alpha=1.0, beta=1.0, fourier_degree=5,
             rec_algorithm='SVTR_LCNet', rec_model_dir='/root/.paddleocr/whl/rec/ch/ch_PP-OCRv3_rec_infer',
             rec_image_inverse=True, rec_image_shape='3, 48, 320', rec_batch_num=6, max_text_length=25,
             rec_char_dict_path='/root/.local/share/virtualenvs/zhongyouOCR-VlF7TM1R/lib/python3.9/site-packages/paddleocr/ppocr/utils/ppocr_keys_v1.txt',
             use_space_char=True, vis_font_path='./doc/fonts/simfang.ttf', drop_score=0.5, e2e_algorithm='PGNet',
             e2e_model_dir=None, e2e_limit_side_len=768, e2e_limit_type='max', e2e_pgnet_score_thresh=0.5,
             e2e_char_dict_path='./ppocr/utils/ic15_dict.txt', e2e_pgnet_valid_set='totaltext',
             e2e_pgnet_mode='fast', use_angle_cls=True,
             cls_model_dir='/root/.paddleocr/whl/cls/ch_ppocr_mobile_v2.0_cls_infer', cls_image_shape='3, 48, 192',
             label_list=['0', '180'], cls_batch_num=6, cls_thresh=0.9, enable_mkldnn=False, cpu_threads=10,
             use_pdserving=False, warmup=False, sr_model_dir=None, sr_image_shape='3, 32, 128', sr_batch_num=1,
             draw_img_save_dir='./inference_results', save_crop_res=False, crop_res_save_dir='./output',
             use_mp=False, total_process_num=1, process_id=0, benchmark=False, save_log_path='./log_output/',
             show_log=True, use_onnx=False, output='./output', table_max_len=488, table_algorithm='TableAttn',
             table_model_dir=None, merge_no_span_structure=True, table_char_dict_path=None, layout_model_dir=None,
             layout_dict_path=None, layout_score_threshold=0.5, layout_nms_threshold=0.5,
             kie_algorithm='LayoutXLM', ser_model_dir=None, re_model_dir=None, use_visual_backbone=True,
             ser_dict_path='../train_data/XFUND/class_list_xfun.txt', ocr_order_method=None, mode='structure',
             image_orientation=False, layout=True, table=True, ocr=True, recovery=False, use_pdf2docx_api=False,
             lang='ch', det=True, rec=True, type='ocr', ocr_version='PP-OCRv3', structure_version='PP-StructureV2')

    DCU = dict(help='==SUPPRESS==', use_gpu=True, use_xpu=False, use_npu=False, ir_optim=True, use_tensorrt=False,
               min_subgraph_size=15, precision='fp32', gpu_mem=500, gpu_id=0, image_dir=None, page_num=0,
               det_algorithm='DB', det_model_dir='/data/cpf/data/models/ch_PP-OCRv3_det_infer', det_limit_side_len=960,
               det_limit_type='max', det_box_type='quad', det_db_thresh=0.3, det_db_box_thresh=0.6,
               det_db_unclip_ratio=1.5, max_batch_size=20, use_dilation=False, det_db_score_mode='fast',
               det_east_score_thresh=0.8, det_east_cover_thresh=0.1, det_east_nms_thresh=0.2, det_sast_score_thresh=0.5,
               det_sast_nms_thresh=0.2, det_pse_thresh=0, det_pse_box_thresh=0.85, det_pse_min_area=16, det_pse_scale=1,
               scales=[8, 16, 32], alpha=1.0, beta=1.0, fourier_degree=5, rec_algorithm='SVTR_LCNet',
               rec_model_dir='/data/cpf/data/models/ch_PP-OCRv3_rec_infer', rec_image_inverse=True,
               rec_image_shape='3, 48, 320', rec_batch_num=10, max_text_length=25,
               rec_char_dict_path='/usr/local/lib/python3.9/site-packages/paddleocr/ppocr/utils/ppocr_keys_v1.txt',
               use_space_char=True, vis_font_path='./doc/fonts/simfang.ttf', drop_score=0.5, e2e_algorithm='PGNet',
               e2e_model_dir=None, e2e_limit_side_len=768, e2e_limit_type='max', e2e_pgnet_score_thresh=0.5,
               e2e_char_dict_path='./ppocr/utils/ic15_dict.txt', e2e_pgnet_valid_set='totaltext', e2e_pgnet_mode='fast',
               use_angle_cls=True, cls_model_dir='/data/cpf/data/models/ch_ppocr_mobile_v2.0_cls_infer',
               cls_image_shape='3, 48, 192', label_list=['0', '180'], cls_batch_num=10, cls_thresh=0.9,
               enable_mkldnn=True, cpu_threads=4, use_pdserving=False, warmup=False, sr_model_dir=None,
               sr_image_shape='3, 32, 128', sr_batch_num=1, draw_img_save_dir='./inference_results',
               save_crop_res=False, crop_res_save_dir='./output', use_mp=False, total_process_num=1, process_id=0,
               benchmark=False, save_log_path='./log_output/', show_log=True, use_onnx=False, output='./output',
               table_max_len=488, table_algorithm='TableAttn', table_model_dir=None, merge_no_span_structure=True,
               table_char_dict_path=None, layout_model_dir=None, layout_dict_path=None, layout_score_threshold=0.5,
               layout_nms_threshold=0.5, kie_algorithm='LayoutXLM', ser_model_dir=None, re_model_dir=None,
               use_visual_backbone=True, ser_dict_path='../train_data/XFUND/class_list_xfun.txt', ocr_order_method=None,
               mode='structure', image_orientation=False, layout=True, table=True, ocr=True, recovery=False,
               use_pdf2docx_api=False, invert=False, binarize=False, alphacolor=(255, 255, 255), lang='ch', det=True,
               rec=True, type='ocr', ocr_version='PP-OCRv4', structure_version='PP-StructureV2', zero_copy_run=True)
