import cv2
image = cv2.imread("pic/1.jpg",-1)#读取图片
    # image = cv2.imread(“名字”, 格式)
    # 其中image是读入的图像名称，“名字”指的是需要读取的图片的文件路径及名字。
    # 格式指的是读取的标记————-1表示保持原有的格式不变
    # 0表示将图像调整为单通道的灰度图像
    # 1表示将图像调整为3通道的BGR通道。为默认值
    # 2表示的是当载入的图像额外16位或者32位时，就返回其对应的深度图像；否则，将转换为8为图像
    # 4表示的是以任何可能的颜色格式读取图像
gauss = cv2.GaussianBlur(image, (25, 25), 3)#高斯滤波
cv2.imshow("gauss", gauss)#显示图像
cv2.imwrite('pic/gauss.jpg',gauss)#保存图像
key = cv2.waitKey(0)#窗口暂停
cv2.destroyAllWindows()
