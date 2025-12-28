import cv2
if __name__ == "__main__":
    gray = cv2.imread("pic/gray.jpg", -1)
    # 高斯滤波
    gray = cv2.GaussianBlur(gray, (25, 25), 3)
    # 自适应阈值二值化
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    cv2.imshow("binary", binary)  # 显示图像
    cv2.imwrite('pic/binary.jpg', binary)  # 保存图像
    key = cv2.waitKey(0)  # 窗口暂停
    cv2.destroyAllWindows()