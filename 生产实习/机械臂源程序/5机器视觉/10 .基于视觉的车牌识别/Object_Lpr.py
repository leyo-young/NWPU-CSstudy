from hyperlpr import HyperLPR_plate_recognition
import cv2
from PIL import ImageFont, ImageDraw, Image
import numpy as np

def ocr_lpr(image):
    result = HyperLPR_plate_recognition(image)  # 识别车牌
    print(result)
    plate = result[0][0]  # 车牌号码
    conf = result[0][1]  # 置信度
    pt1 = (result[0][2][0], result[0][2][1])  # 车牌框左上角坐标
    pt2 = (result[0][2][2], result[0][2][3])  # 车牌框右上角坐标
    # 绘制车牌框
    cv2.rectangle(image, pt1=pt1, pt2=pt2, color=(0, 255, 0), thickness=3)
    # 设置需要显示的字体
    fontpath = "font/simsun.ttc"
    font = ImageFont.truetype(fontpath, size=50)  # 字体大小
    image = Image.fromarray(image)
    draw = ImageDraw.Draw(image)
    # 绘制文字信息
    draw.text((20, 20), plate, font=font, fill=(0, 0, 255))
    image = np.array(image)
    cv2.imwrite("pic/result.jpg", image)
    return image

