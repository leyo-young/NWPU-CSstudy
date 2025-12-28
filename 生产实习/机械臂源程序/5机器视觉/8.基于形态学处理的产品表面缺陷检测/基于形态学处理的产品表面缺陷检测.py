import cv2
import numpy as np
import math
#************************************ 自定义函数***************************
#图像逆时针旋转
def Nrotate(angle,valuex,valuey,pointx,pointy):
      angle = (angle/180)*math.pi
      valuex = np.array(valuex)
      valuey = np.array(valuey)
      nRotatex = (valuex-pointx)*math.cos(angle) - (valuey-pointy)*math.sin(angle) + pointx
      nRotatey = (valuex-pointx)*math.sin(angle) + (valuey-pointy)*math.cos(angle) + pointy
      return (nRotatex, nRotatey)
#图像顺时针旋转
def Srotate(angle,valuex,valuey,pointx,pointy):
      angle = (angle/180)*math.pi
      valuex = np.array(valuex)
      valuey = np.array(valuey)
      sRotatex = (valuex-pointx)*math.cos(angle) + (valuey-pointy)*math.sin(angle) + pointx
      sRotatey = (valuey-pointy)*math.cos(angle) - (valuex-pointx)*math.sin(angle) + pointy
      return (sRotatex,sRotatey)
#将四个点做映射
def rotatecordiate(angle,rectboxs,pointx,pointy):
      output = []
      for rectbox in rectboxs:
        if angle>0:
          output.append(Srotate(angle,rectbox[0],rectbox[1],pointx,pointy))
        else:
          output.append(Nrotate(-angle,rectbox[0],rectbox[1],pointx,pointy))
      return output
# 利用四个点坐标进行裁剪
def imagecrop(image, box):
    xs = [x[1] for x in box]
    ys = [x[0] for x in box]
    print(xs)
    print(min(xs), max(xs), min(ys), max(ys))
    cropimage = image[min(xs):max(xs), min(ys):max(ys)]
    print(cropimage.shape)
    cv2.imwrite('pic/cropimage.jpg', cropimage)
    return cropimage
#************************************************************************
def main():
    # 1.读取输入图片
    src= cv2.imread("pic/1.jpg")
    # 2.高斯滤波
    gauss = cv2.GaussianBlur(src, (25, 25),0)
    cv2.imshow("gauss", gauss)
    # 3.转灰度图
    gray = cv2.cvtColor(gauss, cv2.COLOR_BGR2GRAY)
    cv2.imshow("gray", gray)
    #4.自适应阈值分割（图像二值化）
    threshold = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    element1 = cv2.getStructuringElement(cv2.MORPH_RECT, (6, 5))
    element2 = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    threshold = cv2.erode(threshold, element1)#腐蚀
    threshold = cv2.dilate(threshold, element2)#膨胀
    cv2.imshow("threshold", threshold)
    #5.找轮廓
    contours, hierarchy = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    #6.遍历轮廓，根据轮廓面积等判断，求取最小外接矩形等
    for cnt in contours:
        # 获取轮廓面积
        area = cv2.contourArea(cnt)
        print("轮廓像素面积:", area)  # 打印所有轮廓面积
        # 当面积大于3000，代表有形状存在
        if area > 15000:
            print("轮廓像素面积:", area)  # 打印符合条件轮廓面积
            rect = cv2.minAreaRect(cnt)  # 最小外接矩形
            box = cv2.boxPoints(rect)  # boxPoints返回四个点顺序：右下→左下→左上→右上
            box = np.int0(box)
            M = cv2.getRotationMatrix2D(rect[0], rect[2], 1)#取得旋转角度的矩阵M
            dst = cv2.warpAffine(src, M, (2 * src.shape[0], 2 * src.shape[1]))#图像仿射变换
            newbox = rotatecordiate(rect[2], box, rect[0][0], rect[0][1])#根据角度与原来矩形框做映射，旋转图像
            image1 = imagecrop(dst, np.int0(newbox))#裁剪图像
            cv2.imshow("image1", image1)
            gauss_image1 = cv2.GaussianBlur(image1, (7, 7), 0)
            cv2.imshow("gauss_image1", gauss_image1)
            gray_image1 = cv2.cvtColor(gauss_image1, cv2.COLOR_BGR2GRAY)
            ret, threshold_image1 = cv2.threshold(gray_image1, 0, 150, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            cv2.imshow("threshold_image1", threshold_image1)
            # 7.创建操作核，执行闭操作并显示
            kernel = np.ones((5, 5), np.uint8)
            img_close = cv2.morphologyEx(threshold_image1, cv2.MORPH_CLOSE, kernel)#闭运算，先膨胀再腐蚀
            cv2.imshow("img_close", img_close)
            # 8.图像相减并显示
            img_deal=img_close-threshold_image1#使用没有缺陷的图和有缺陷的图做差，得到只有缺陷的图
            cv2.imshow("img_deal", img_deal)
            # 9.开运算并显示
            kernel2 = np.ones((3,7),np.uint8)
            dilation = cv2.dilate(img_deal,kernel2,iterations = 1)
            cv2.imshow("dilation", dilation)
            #10.提取轮廓
            canny = cv2.Canny(dilation, 1, 255)
            contours, hierarchy = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            #11.绘制所有轮廓
            for cnt in range(len(contours)):
                cv2.drawContours(image1, contours, cnt, (0, 255, 0), 1)  # 提取与绘制轮廓
                # 筛选前打印轮廓大小
                for i in contours:
                    print("contourArea",cv2.contourArea(i))
                # 设置筛选条件
                contours0 = [i for i in contours if cv2.contourArea(i) > 10]
                # 筛选后打印轮廓大小
                for i in contours0:
                    print(cv2.contourArea(i))
            cv2.imshow("result", image1)
            cv2.imwrite("pic/result.jpg",image1)
            cv2.waitKey(0)
            cv2.destroyALLWindows()
if __name__ == "__main__":
    main()

