import cv2 as cv
from math import sqrt

global img #全局变量 img图像
global point1, point2 #全局变量 图像中的两点
def on_mouse(event, x, y, flag, param):#鼠标点击事件函数
    global img, point1, point2
    img2 = img.copy()
    if event == cv.EVENT_LBUTTONDOWN:  # 左键点击
        point1 = (x, y)
        cv.circle(img2, point1, 10, (0, 255, 0), 5)#鼠标点击的位置画圈
        cv.imshow('image', img2)
    elif event == cv.EVENT_MOUSEMOVE and (flag & cv.EVENT_FLAG_LBUTTON):  # 按住左键拖曳
        cv.line(img2, point1, (x, y), (255, 0, 0), 2)#开始画线
        cv.imshow('image', img2)
    elif event == cv.EVENT_LBUTTONUP:  # 左键释放
        point2 = (x, y)
        cv.line(img2, point1, point2, (255, 0, 0), 5)
        cv.imshow('image', img2)
        pixel_distance = sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)#计算两点之间的像素距离
        cv.putText(img2, "pixel_distance:" + str(round(pixel_distance)), (10, 20), cv.FONT_HERSHEY_COMPLEX, 0.5,
                   (0, 0, 255), 1)#将距离写在图像上
        cv.imshow('image', img2)
        cv.imwrite("pic/result.jpg", img2)  # 保存结果
        print("pixel_distance:", pixel_distance)
    elif event == cv.EVENT_RBUTTONDOWN:  # 右键点击,刷新图像
        cv.imshow('image', img2)
if __name__ == "__main__":
    img = cv.imread('pic/1.jpg')  # 此处更改图片路径
    cv.namedWindow('image')
    cv.setMouseCallback('image', on_mouse)
    cv.imshow('image', img)
    cv.waitKey(0)
    cv.destroyAllWindows()
