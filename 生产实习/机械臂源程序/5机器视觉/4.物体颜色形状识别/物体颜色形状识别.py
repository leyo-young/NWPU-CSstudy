import cv2
import numpy as np
import math

# 图像预处理
def img_Threshold(src_gauss):
    imgHSV = cv2.cvtColor(src_gauss, cv2.COLOR_BGR2HSV)
    cv2.imshow("imgHSV", imgHSV)
    # # 三通道分割
    h, s, v = cv2.split(imgHSV)
    # 检测差值
    hs_diff = cv2.absdiff(h, s)
    cv2.imshow("hs_diff", hs_diff)
    sv_diff = cv2.absdiff(s, v)
    cv2.imshow("sv_diff", sv_diff)
    hv_diff = cv2.absdiff(h, v)
    cv2.imshow("hv_diff", hv_diff)
    v1 = np.mean(hs_diff)  # 取每个通道的均值
    v2 = np.mean(sv_diff)
    v3 = np.mean(hv_diff)
    v_max = (v1 if v1 > v2 else v2) if (v1 if v1 > v2 else v2) > v3 else v3  # 比较均值得到最大值
    print(v_max, v3)
    if v_max > 8:
        if abs(v_max - v1) < 0.01:
            gray = hs_diff.copy()
        elif abs(v_max - v2) < 0.01:
            gray = sv_diff.copy()
        elif abs(v_max - v3) < 0.01:
            gray = hv_diff.copy()
    return gray
# 图像开运算和闭运算(形态学处理)
def img_dila_eros(src_img):
    # 3. 膨胀和腐蚀操作的核函数
    element1 = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 3))
    element2 = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 3))
    element3 = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    # 4. 膨胀一次，让轮廓突出
    src_img = cv2.dilate(src_img, element2)
    # 5. 腐蚀一次，去掉细节，如表格线等。注意这里去掉的是竖直的线
    src_img = cv2.erode(src_img, element1)
    # 6. 再次膨胀，让轮廓明显一些
    src_img = cv2.dilate(src_img, element2)
    src_img = cv2.morphologyEx(src_img, cv2.MORPH_OPEN, element3)  # 开运算去掉噪点
    return src_img
# 颜色识别
def recognize_color(src_img):
    hsvRoi = cv2.cvtColor(src_img, cv2.COLOR_BGR2HSV)
    print('min H = {}, min S = {}, min V = {}; max H = {}, max S = {}, max V = {}'.format(hsvRoi[:, :, 0].min(),hsvRoi[:, :, 1].min(),hsvRoi[:, :, 2].min(),hsvRoi[:, :, 0].max(),hsvRoi[:, :, 1].max(),hsvRoi[:, :, 2].max()))
    mean = np.array([hsvRoi[:, :, 0].mean(), hsvRoi[:, :, 1].mean(), hsvRoi[:, :, 2].mean()])
    print("mean:", mean)
    H = mean[0]
    S = mean[1]
    V = mean[2]
    if (((H >= 0 and H <= 20) or (H >= 156 and H <= 180)) and S >= 43 and S <= 255 and V >= 46 and V <= 255):
        color = "red"
    elif (H >= 20 and H <= 44 and S >= 43 and S <= 255 and V >= 46 and V <= 255):
        color = "Yellow"
    elif (H >= 95 and H <= 124 and S >= 43 and S <= 255 and V >= 46 and V <= 255):
        color = "blue"
    elif (H >= 45 and H <= 80 and S >= 43 and S <= 255 and V >= 46 and V <= 255):
        color = "Green"
    elif (H >= 0 and H <= 180 and S >= 0 and S <= 255 and V >= 0 and V <= 46):
        color = "Black"
    elif (H >= 0 and H <= 180 and S >= 0 and S <= 43 and V >= 46 and V <= 220):
        color = "White"
    elif (H >= 11 and H <= 25 and S >= 43 and S <= 255 and V >= 46 and V <= 255):
        color = "Orange"
    elif (H >= 78 and H <= 95 and S >= 43 and S <= 255 and V >= 46 and V <= 255):
        color = "Cyan"
    elif (H >= 125 and H <= 155 and S >= 43 and S <= 255 and V >= 46 and V <= 255):
        color = "Purple"
    else:
        color = "None"
    print("color:", color)
    return color
# 图像逆时针旋转
def Nrotate(angle, valuex, valuey, pointx, pointy):
    angle = (angle / 180) * math.pi
    valuex = np.array(valuex)
    valuey = np.array(valuey)
    nRotatex = (valuex - pointx) * math.cos(angle) - (valuey - pointy) * math.sin(angle) + pointx
    nRotatey = (valuex - pointx) * math.sin(angle) + (valuey - pointy) * math.cos(angle) + pointy
    return (nRotatex, nRotatey)
# 图像顺时针旋转
def Srotate(angle, valuex, valuey, pointx, pointy):
    angle = (angle / 180) * math.pi
    valuex = np.array(valuex)
    valuey = np.array(valuey)
    sRotatex = (valuex - pointx) * math.cos(angle) + (valuey - pointy) * math.sin(angle) + pointx
    sRotatey = (valuey - pointy) * math.cos(angle) - (valuex - pointx) * math.sin(angle) + pointy
    return (sRotatex, sRotatey)
# 将四个点做映射
def rotatecordiate(angle, rectboxs, pointx, pointy):
    output = []
    for rectbox in rectboxs:
        if angle > 0:
            output.append(Srotate(angle, rectbox[0], rectbox[1], pointx, pointy))
        else:
            output.append(Nrotate(-angle, rectbox[0], rectbox[1], pointx, pointy))
    return output
# 利用四个点坐标进行裁剪
def imagecrop(image, box):
    xs = [x[1] for x in box]
    ys = [x[0] for x in box]
    cropimage = image[min(xs):max(xs), min(ys):max(ys)]
    cv2.imwrite('pic/cropimage.jpg', cropimage)
    return cropimage
# 形状检测
def getContours(src, img):
    # 查找轮廓，cv2.RETR_ExTERNAL=获取外部轮廓点, CHAIN_APPROX_NONE = 得到所有的像素点,CHAIN_APPROX_SIMPLE=得到轮廓的四个点
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # 循环轮廓，判断每一个形状
    for cnt in contours:
        # 获取轮廓面积
        area = cv2.contourArea(cnt)
        # print("轮廓像素面积:", area)  # 打印所有轮廓面积
        # 当面积大于20000，代表有形状存在
        if area > 20000:
            # print("轮廓像素面积:", area)  # 打印符合条件轮廓面积
            # 计算所有轮廓的周长，便于做多边形拟合
            # 多边形拟合，获取每个形状的边
            approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)  # 拟合的多边形的边数
            print("approx:", len(approx))
            objCor = len(approx)  # 轮廓的边长
            rect = cv2.minAreaRect(approx)  # 最小外接矩形
            box = cv2.boxPoints(rect)  # boxPoints返回四个点顺序：右下→左下→左上→右上
            box = np.int0(box)
            center = rect[0]  # 中心坐标
            center_array = np.array(center)
            int_center = center_array.astype(int)
            width = rect[1][0]  # 矩形宽
            height = rect[1][1]  # 矩形高
            angle = rect[2]  # 旋转角度
            print("中心：{0}, 宽：{1}, 高：{2}, 角度：{3}".format(center, width, height, angle))
            M = cv2.getRotationMatrix2D(rect[0], rect[2], 1)#获得仿射变换矩阵，rect[0]表示中间的位置，rect[2]表示旋转的角度，1表示等比例缩放
            dst = cv2.warpAffine(src, M, (2 * src.shape[0], 2 * src.shape[1]))#进行仿射变换，src表示输入图像，M仿射变换矩阵，(2 * src.shape[0], 2 * src.shape[1])表示仿射变换后的图像大小，为防止图像旋转超出边界故设置为原来的两倍
            newbox = rotatecordiate(rect[2], box, rect[0][0], rect[0][1])#对原图ROI图像box做映射到新newbox
            image1 = imagecrop(dst, np.int0(newbox))#在仿射变换后的图像上裁剪newbox图像得到物体摆正后的ROI图
            cv2.imshow("image1", image1)
            color = recognize_color(image1)  # left_up_y, left_down_y, left_up_x, right_up_x
            # 画出边界
            if objCor > 4:
                cv2.circle(src, (int(rect[0][0]), int(rect[0][1])), int(rect[1][0] / 2), (255, 255, 255), 5)
            else:
                cv2.drawContours(src, [box], 0, (255, 255, 255), 3)  # 画出多边形形状
            cv2.circle(src, (int(rect[0][0]), int(rect[0][1])), 3, (255, 255, 255), 5)
            # 计算出边界后，即边数代表形状，如三角形边数=3
            if objCor == 3:
                objectType = "Tri"  # 三角形
            elif objCor == 4:
                # 判断是矩形还是正方形
                aspRatio = rect[1][0] / float(rect[1][1])
                print("aspRatio:", aspRatio)
                if aspRatio > 0.9 and aspRatio < 1.1:
                    objectType = "Square"  # 正方形
                else:
                    objectType = "Rectangle"  # 矩形
            # 大于4个边的就是圆形
            elif objCor > 4:
                objectType = "Circles"  # 圆形
            else:
                objectType = "None"
            cv2.putText(src, "center:" + str(int_center), (10, 20), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1)
            cv2.putText(src, "width:" + str(round(width)), (10, 40), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1)
            cv2.putText(src, "height:" + str(round(height)), (10, 60), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1)
            cv2.putText(src, "shape:" + objectType, (10, 80), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1)
            cv2.putText(src, "color:" + color, (10, 100), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1)
            cv2.putText(src, "area:" + str(area), (10, 120), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1)
            if objCor <= 4:
                cv2.putText(src, "angle:" + str(round(angle)), (10, 140), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1)
if __name__ == "__main__":
    # 读取图片
    image = cv2.imread("pic/4.jpg")
    # 图片复制不改变原图
    src_img = image.copy()
    cv2.imshow("image", image)
    # 高斯滤波
    gauss = cv2.GaussianBlur(src_img, (15, 15), 3)
    cv2.imshow("gauss", gauss)
    # 图像预处理
    gray = img_Threshold(gauss)
    # 高斯滤波
    gray = cv2.GaussianBlur(gray, (15, 15), 3)
    cv2.imshow("gray", gray)
    # 自适应阈值二值化
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    # 图像形态学处理
    binary = img_dila_eros(binary)
    cv2.imshow("binary", binary)
    # 获取轮廓 计算中心点坐标，尺寸；形状识别，颜色识别。
    getContours(image, binary)
    cv2.imwrite("pic/result.jpg",image)
    cv2.imshow("result", image)
    key = cv2.waitKey(0)
