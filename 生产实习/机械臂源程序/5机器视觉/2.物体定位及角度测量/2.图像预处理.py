import cv2
import numpy as np
# 图像预处理
def img_Threshold(src_gauss):
    imgHSV = cv2.cvtColor(src_gauss, cv2.COLOR_BGR2HSV)
    # gray1=cv2.cvtColor(src_gauss,cv2.COLOR_BGR2GRAY)
    # cv2.imshow("gray1", gray1)
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
if __name__ == "__main__":
    gauss = cv2.imread("pic/gauss.jpg", -1)
    # 图像预处理
    gray = img_Threshold(gauss)
    # 高斯滤波
    gray = cv2.GaussianBlur(gray, (15, 15), 3)
    cv2.imshow("gray", gray)  # 显示图像
    cv2.imwrite('pic/gray.jpg', gray)  # 保存图像
    key = cv2.waitKey(0)  # 窗口暂停
    cv2.destroyAllWindows()
