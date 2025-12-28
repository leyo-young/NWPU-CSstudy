import cv2
# 图像开运算和闭运算(形态学处理)
def img_dila_eros(src_img):
    # 3. 膨胀和腐蚀操作的核函数
    element1 = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 3))
    element2 = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 3))
    element3 = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    # 4. 膨胀一次，让轮廓突出
    src_img = cv2.dilate(src_img, element2)
    # 5. 腐蚀一次，去掉细节，如表格线等。注意这里去掉的是竖直的线
    src_img = cv2.erode(src_img, element1)
    # 6. 再次膨胀，让轮廓明显一些
    # src_img = cv2.dilate(src_img, element2)
    src_img = cv2.morphologyEx(src_img, cv2.MORPH_OPEN, element3)#开运算去掉噪点
    return src_img
if __name__ == "__main__":
    binary = cv2.imread("pic/binary.jpg", -1)
    # 图像形态学处理
    dila_eros = img_dila_eros(binary)
    cv2.imshow("dila_eros", dila_eros)
    cv2.imwrite('pic/dila_eros.jpg', dila_eros)  # 保存图像
    key = cv2.waitKey(0)  # 窗口暂停
    cv2.destroyAllWindows()
