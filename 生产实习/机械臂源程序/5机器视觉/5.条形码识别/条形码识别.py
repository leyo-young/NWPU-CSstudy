# coding=utf-8
# 导入python包
import numpy as np
import argparse
import imutils
import cv2
from pyzbar import pyzbar

# 读取图片并将其转化为灰度图片
image = cv2.imread("pic/1.jpg")
image1 = image.copy()#复制图像用于显示结果图
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# 计算图像中x和y方向的Scharr梯度幅值表示
ddepth = cv2.cv.CV_32F if imutils.is_cv2() else cv2.CV_32F
gradX = cv2.Sobel(gray, ddepth=ddepth, dx=1, dy=0, ksize=-1)
gradY = cv2.Sobel(gray, ddepth=ddepth, dx=0, dy=1, ksize=-1)
# x方向的梯度减去y方向的梯度
gradient = cv2.subtract(gradX, gradY)
# 获取处理后的绝对值
gradient = cv2.convertScaleAbs(gradient)
cv2.imwrite("pic/gradient.jpg", gradient)
# 对处理后的结果进行模糊操作
blurred = cv2.blur(gradient, (9, 9))
# 将其转化为二值图片
(_, thresh) = cv2.threshold(blurred, 180, 255, cv2.THRESH_BINARY)#条形码图像二值化，如果检测框小则将阈值调低，反之调大
cv2.imwrite("pic/thresh.jpg", thresh)
# 构建一个掩码并将其应用在二值图片中
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 7))
closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
cv2.imwrite("pic/closed1.jpg", closed)
# 执行多次膨胀和腐蚀操作
closed = cv2.erode(closed, None, iterations = 4)
closed = cv2.dilate(closed, None, iterations = 4)
cv2.imwrite("pic/closed2.jpg", closed)
# 在二值图像中寻找轮廓, 然后根据他们的区域大小对该轮廓进行排序，保留最大的一个轮廓
cnts = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
c = sorted(cnts, key = cv2.contourArea, reverse = True)[0]
# 计算最大的轮廓的最小外接矩形
rect = cv2.minAreaRect(c)
box = cv2.cv.BoxPoints(rect) if imutils.is_cv2() else cv2.boxPoints(rect)
box = np.int0(box)
# 绘制并显示结果
cv2.drawContours(image1, [box], -1, (0, 255, 0), 3)
result = np.hstack([image, image1])
#输出条形码
barcodes = pyzbar.decode(result)
for barcode in barcodes:
    barcodeData = barcode.data.decode("utf-8")
    cv2.putText(image1, barcodeData, (50, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
cv2.imwrite("pic/detect_result.jpg", image1)
cv2.imshow("result", image1)
cv2.waitKey(0)
cv2.destroyAllWindows()