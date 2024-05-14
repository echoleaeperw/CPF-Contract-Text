import cv2


def draw_rectangle_paddle(image_path, rectangles):
    # 读取图像
    image = cv2.imread(image_path)

    # 直接在图像上绘制所有矩形
    for top_left, bottom_right in rectangles:
        cv2.rectangle(image, top_left, bottom_right, (0, 0, 255), 4)

    # 保存图像
    cv2.imwrite(image_path, image)
