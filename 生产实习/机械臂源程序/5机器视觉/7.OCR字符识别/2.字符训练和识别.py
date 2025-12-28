import cv2
import numpy as np
import operator
import os
# 模块级变量 ###########################
#小字符面积阈值范围
MIN_CONTOUR_AREA = 150 #轮廓的面积阈值参数，用于选取此阈值范围内的矩形框，滤出多余干扰
MAX_CONTOUR_AREA = 650
#大字符面积阈值范围
MIN_CONTOUR_AREA_single = 2500
MAX_CONTOUR_AREA_single = 6000
#创建的空模板图像的大小
RESIZED_IMAGE_WIDTH = 20
RESIZED_IMAGE_HEIGHT = 30

class ContourWithData():
    # 成员变量
    npaContour = None  # 轮廓
    boundingRect = None  # 轮廓的边界矩形
    intRectX = 0  # 边界矩形左上角x位置
    intRectY = 0  # 边界矩形左上角y位置
    intRectWidth = 0  # 边界矩形宽度
    intRectHeight = 0  # 边界矩形高度
    fltArea = 0.0  # 等高线面积

    def calculateRectTopLeftPointAndWidthAndHeight(self):  # 计算边界矩形信息
        [intX, intY, intWidth, intHeight] = self.boundingRect
        self.intRectX = intX
        self.intRectY = intY
        self.intRectWidth = intWidth
        self.intRectHeight = intHeight

    def checkIfContourIsValid(self):  # 增加此判断增强程序健壮性
        if self.fltArea > MIN_CONTOUR_AREA: return True  # 更好的有效性检查
        return False
def main():
    allContoursWithData = []  # 声明空列表
    validContoursWithData = []
    try:
        npaClassifications = np.loadtxt("classifications.txt", np.float32)  # 读入训练分类
    except:
        print("error, unable to open classifications.txt, exiting program\n")
        os.system("pause")
        return
    try:
        npaFlattenedImages = np.loadtxt("flattened_images.txt", np.float32)  # 读入训练图像
    except:
        print("error, unable to open flattened_images.txt, exiting program\n")
        os.system("pause")
        return
    npaClassifications = npaClassifications.reshape((npaClassifications.size, 1))  # 将 numpy 数组重塑为 1d，需要通过调用来训练
    kNearest = cv2.ml.KNearest_create()  # 实例化 KNN 对象
    kNearest.train(npaFlattenedImages, cv2.ml.ROW_SAMPLE, npaClassifications)#训练字符
    imgTestingNumbers = cv2.imread("pic/1.jpg")  # 读入测试数字图像
    if imgTestingNumbers is None:  # 如果图像未成功读取
        print("error: image not read from file \n\n")  # 将错误消息打印到标准输出
        os.system("pause")  # 暂停，以便用户可以看到错误消息
        return  # 和退出函数（退出程序）
    imgGray = cv2.cvtColor(imgTestingNumbers, cv2.COLOR_BGR2GRAY)  # 获取灰度图像
    imgBlurred = cv2.GaussianBlur(imgGray, (29, 29), 0)  # 高斯滤波
    # 图像自适应阈值二值化
    imgThresh = cv2.adaptiveThreshold(imgBlurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    # imgThresh = cv2.GaussianBlur(imgThresh, (25, 25), 1)  # 高斯滤波
    element1 = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 3))
    element2 = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 3))
    element3 = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    # 4. 膨胀一次，让轮廓突出
    imgThresh = cv2.dilate(imgThresh, element2)
    # 5. 腐蚀一次，去掉细节，如表格线等。注意这里去掉的是竖直的线
    imgThresh = cv2.erode(imgThresh, element1)
    imgThresh = cv2.morphologyEx(imgThresh, cv2.MORPH_OPEN, element3)  # 开运算去掉噪点
    imgThreshCopy = imgThresh.copy()  # 制作 imgThresh 图像的副本，这在必要时 findContours 会修改图像
    npaContours, npaHierarchy = cv2.findContours(imgThreshCopy, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for npaContour in npaContours:  # 对于每个轮廓
        if(cv2.contourArea(npaContour) > MIN_CONTOUR_AREA and cv2.contourArea(npaContour) < MAX_CONTOUR_AREA):#小字符面积判断
        # if(cv2.contourArea(npaContour) > MIN_CONTOUR_AREA_single and cv2.contourArea(npaContour) < MAX_CONTOUR_AREA_single):#大字符面积判断
            print(cv2.contourArea(npaContour))
            contourWithData = ContourWithData()  # 用数据对象实例化轮廓
            contourWithData.npaContour = npaContour  # 将轮廓分配给带有数据的轮廓
            contourWithData.boundingRect = cv2.boundingRect(contourWithData.npaContour)  # 得到边界矩形,函数 cv2.minAreaRect() 返回一个Box2D结构rect：（最小外接矩形的中心（x，y），（宽度，高度），旋转角度）
            contourWithData.calculateRectTopLeftPointAndWidthAndHeight()  # 获取边界矩形信息
            contourWithData.fltArea = cv2.contourArea(contourWithData.npaContour)  # 计算轮廓面积
            allContoursWithData.append(contourWithData)  # 将带有数据对象的轮廓添加到带有数据的所有轮廓的列表中
    for contourWithData in allContoursWithData:  # 适用于所有轮廓
        if contourWithData.checkIfContourIsValid():  # 检查是否有效
            validContoursWithData.append(contourWithData)  # 如果是这样，附加到有效的轮廓列表
    validContoursWithData.sort(key=operator.attrgetter("intRectX"))  # 从左到右对轮廓进行排序
    strFinalString = ""  # 声明最终字符串，这将在程序结束时具有最终的数字序列
    for contourWithData in validContoursWithData:  # 对于每个轮廓
        # 在当前字符周围绘制一个绿色矩形
        cv2.rectangle(imgTestingNumbers, (contourWithData.intRectX, contourWithData.intRectY), (
        contourWithData.intRectX + contourWithData.intRectWidth,
        contourWithData.intRectY + contourWithData.intRectHeight), (0, 255, 0), 2)
        imgROI = imgThresh[contourWithData.intRectY: contourWithData.intRectY + contourWithData.intRectHeight,
                 contourWithData.intRectX: contourWithData.intRectX + contourWithData.intRectWidth]  # 从阈值图像中裁剪出字符
        imgROIResized = cv2.resize(imgROI, (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT))  # 调整图像大小，这将更一致的识别和存储
        npaROIResized = imgROIResized.reshape((1, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))  # 将图像展平为一维 numpy 数组
        npaROIResized = np.float32(npaROIResized)  # 从一维 numpy 整数数组转换为一维 numpy 浮点数组
        retval, npaResults, neigh_resp, dists = kNearest.findNearest(npaROIResized, k=1)  # 调用 KNN 函数 find_nearest
        strCurrentChar = str(chr(int(npaResults[0][0])))  # 从结果中获取字符
        cv2.putText(imgTestingNumbers, str(strCurrentChar),
                    (int(contourWithData.intRectX + contourWithData.intRectWidth / 2), int(contourWithData.intRectY)),
                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1)
        strFinalString = strFinalString + strCurrentChar  # 将当前字符附加到完整字符串
    print("\n" + strFinalString + "\n")  # 显示完整的字符串
    cv2.imshow("imgTestingNumbers", imgTestingNumbers)  # 显示输入图像，在找到的数字周围绘制绿色框
    cv2.imwrite("pic/result.jpg",imgTestingNumbers)#保存识别结果图像
    cv2.waitKey(0)  # 等待用户按键
    cv2.destroyAllWindows()  # 从内存中删除窗口
    return
if __name__ == "__main__":
    main()
