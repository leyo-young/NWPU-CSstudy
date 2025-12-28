import cv2
import numpy as np
# 定位和角度测量
def getContours(src, img):
    # 查找轮廓，cv2.RETR_ExTERNAL=获取外部轮廓点, CHAIN_APPROX_NONE = 得到所有的像素点,CHAIN_APPROX_SIMPLE=得到轮廓的四个点
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # 循环轮廓，判断每一个形状
    for cnt in contours:
        # 获取轮廓面积
        area = cv2.contourArea(cnt)
        print("轮廓像素面积:", area)  # 打印所有轮廓面积
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
            angle = rect[2]  # 旋转角度
            # 画出边界
            if objCor > 4:
                cv2.circle(src, (int(rect[0][0]), int(rect[0][1])), int(rect[1][0] / 2), (255, 255, 255), 5)
            else:
                cv2.drawContours(src, [box], 0, (255, 255, 255), 3)  # 画出多边形形状
            cv2.circle(src, (int(rect[0][0]), int(rect[0][1])), 3, (255, 255, 255), 5)
            # 画中心，写角度
            cv2.putText(src, "center:" + str(int_center), (10, 20), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1)
            if objCor <= 4:
                cv2.putText(src, "angle:" + str(round(angle)), (10, 40), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1)
            else:
                cv2.putText(src, "angle:" + "0", (10, 40), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1)
if __name__ == "__main__":
    dila_eros = cv2.imread("pic/dila_eros.jpg", -1)
    result = cv2.imread("pic/1.jpg", -1)  # 读取原图
    # 定位和角度测量
    getContours(result, dila_eros)
    cv2.imshow("result", result)
    cv2.imwrite('pic/result.jpg', result)  # 保存图像
    key = cv2.waitKey(0)  # 窗口暂停
    cv2.destroyAllWindows()
