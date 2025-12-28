import sys
import numpy as np
import cv2
import os

# 模块变量
MIN_CONTOUR_AREA = 100#轮廓的面积阈值参数，用于选取此阈值范围内的矩形框，滤出多余干扰
MAX_CONTOUR_AREA = 8000

RESIZED_IMAGE_WIDTH = 20#创建的空模板图像的大小
RESIZED_IMAGE_HEIGHT = 30

def main():
    imgTrainingNumbers = cv2.imread("pic/training_chars.jpg")  # 读入训练数字图像模板
    if imgTrainingNumbers is None:  # 如果图像未成功读取
        print("error: image not read from file \n\n")  # 将错误消息打印到标准输出
        os.system("pause")  # 暂停，以便用户可以看到错误消息
        return  # 和退出函数（退出程序）
    imgGray = cv2.cvtColor(imgTrainingNumbers, cv2.COLOR_BGR2GRAY)  # 获取灰度图像
    imgBlurred = cv2.GaussianBlur(imgGray, (5, 5), 0)  # 高斯滤波
    # 自适应阈值分割
    imgThresh = cv2.adaptiveThreshold(imgBlurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    cv2.imshow("imgThresh", imgThresh)  # 显示阈值图像
    imgThreshCopy = imgThresh.copy()  # 制作 imgThresh 图像的副本，这在必要时 findContours 会修改图像
    # 输入图像，请确保使用副本，因为该函数会在查找轮廓的过程中修改此图像,仅检索最外面的轮廓,压缩水平、垂直和对角线段，只保留它们的端点
    npaContours, npaHierarchy = cv2.findContours(imgThreshCopy, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # 声明空的 numpy 数组，稍后我们将使用它来写入文件
    # 零行，足够的列来保存所有图像数据
    npaFlattenedImages = np.empty((0, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))
    intClassifications = []  # 声明空分类列表，这将是我们如何根据用户输入对字符进行分类的列表，我们将在最后写入文件
    # 我们感兴趣的可能字符是数字0-9,a-z,A-Z，将它们放入列表 intValidChars
    intValidChars = [ord('0'), ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6'), ord('7'), ord('8'), ord('9')
        , ord('A'), ord('B'), ord('C'), ord('D'), ord('E'), ord('F'), ord('G'), ord('H'), ord('I'), ord('J')
        , ord('K'), ord('L'), ord('M'), ord('N'), ord('O'), ord('P'), ord('Q'), ord('R'), ord('S'), ord('T')
        , ord('U'), ord('V'), ord('W'), ord('X'), ord('Y'), ord('Z')
        , ord('a'), ord('b'), ord('c'), ord('d'), ord('e'), ord('f'), ord('g'), ord('h'), ord('i'), ord('j')
        , ord('k'), ord('l'), ord('m'), ord('n'), ord('o'), ord('p'), ord('q'), ord('r'), ord('s'), ord('t')
        , ord('u'), ord('v'), ord('w'), ord('x'), ord('y'), ord('z')]
    for npaContour in npaContours:  # 对于每个轮廓
        if cv2.contourArea(npaContour) > MIN_CONTOUR_AREA and cv2.contourArea(npaContour) < MAX_CONTOUR_AREA:  #根据轮廓的面积来判断分割的字符
            [intX, intY, intW, intH] = cv2.boundingRect(npaContour)  # 获取并突破边界矩形
            # 当我们要求用户输入时，在每个轮廓周围绘制矩形
            cv2.rectangle(imgTrainingNumbers, (intX, intY), (intX + intW, intY + intH), (0, 0, 255), 2)
            imgROI = imgThresh[intY:intY + intH, intX:intX + intW]  # 从阈值图像中裁剪出字符
            imgROIResized = cv2.resize(imgROI, (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT))  # 调整图像大小，这将更一致的识别和存储
            cv2.imshow("imgROI", imgROI)  # 显示裁剪出来的字符以供参考
            cv2.imshow("imgROIResized", imgROIResized)  # 显示调整大小的图像以供参考
            cv2.imshow("training_numbers.jpg", imgTrainingNumbers)  # 显示训练数字图像，现在将在其上绘制红色矩形
            intChar = cv2.waitKey(0)  # 通过键盘输入给每个分割出来的字符贴上对应名称标签，作为分类训练的模板数据
            if intChar == 27:  # 如果按下 esc 键
                sys.exit()  # 退出程序
            elif intChar in intValidChars:  # 否则，如果该字符在我们正在寻找的字符列表中
                intClassifications.append(intChar)  # 将分类字符附加到字符的整数列表（稍后我们将在写入文件之前转换为浮点数）
                npaFlattenedImage = imgROIResized.reshape((1, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))  # 将图像展平为 1d numpy 数组，以便我们稍后写入文件
                npaFlattenedImages = np.append(npaFlattenedImages, npaFlattenedImage,0)  # 将当前展平图像 numpy 数组添加到展平图像 numpy 数组列表
    fltClassifications = np.array(intClassifications, np.float32)  # 将整数的分类列表转换为浮点数的 numpy 数组
    npaClassifications = fltClassifications.reshape((fltClassifications.size, 1))  # 将浮点数的 numpy 数组展平为 1d，以便我们稍后写入文件
    print("\n\ntraining complete !!\n")
    np.savetxt("classifications.txt", npaClassifications)  # 分类器结果保存
    np.savetxt("flattened_images.txt", npaFlattenedImages)  #OCR模板图片数据保存
    cv2.destroyAllWindows()
    return
if __name__ == "__main__":
    main()
