import cv2
import numpy as np

def undistort(frame):
    #内参数矩阵
    fx = 4.93893672e+04
    cx = 3.17913049e+02
    fy = 3.96661875e+04
    cy = 2.40655992e+02
    # 畸变系数
    k1, k2, p1, p2, k3 =-5.25760326e+01 , -5.88466988e-01 , 3.22153024e-01 ,-7.78611285e-03 ,2.38687870e-01

    # 相机坐标系到像素坐标系的转换矩阵
    k = np.array([
        [fx, 0, cx],
        [0, fy, cy],
        [0, 0, 1]
    ])
    # 畸变系数
    d = np.array([
        k1, k2, p1, p2, k3
    ])
    h, w = frame.shape[:2]
    mapx, mapy = cv2.initUndistortRectifyMap(k, d, None, k, (w, h), 5)#计算无畸变和修正转换映射
    return cv2.remap(frame, mapx, mapy, cv2.INTER_LINEAR)
# 对摄像头实时视频流做畸变矫正
def distortion_correction_cam():
    cap = cv2.VideoCapture(0)  # 准备获取图像
    ret, image = cap.read()
    if ret != True:
        cap = cv2.VideoCapture(3) # 由于系统初始化USB口是随机顺序,USB相机的端口号可能是0或者3
    # 获取摄像头读取画面的宽和高
    width = cap.get(3)
    height = cap.get(4)
    fps = cap.get(5)
    print(width, height, fps)  # 640.0 480.0 30.0

    # 在这里把摄像头的分辨率修改为和我们标定时使用的一样的分辨率 640x480
    cap.set(3, 640)
    cap.set(4, 480)
    width = cap.get(3)
    height = cap.get(4)
    print(width, height, fps)  # 640.0 480.0 30.0

    while (cap.isOpened()):
        ret, frame = cap.read()
        print(frame.shape)
        undistort_frame = undistort(frame)#图像校正
        compare = np.hstack((frame, undistort_frame))#图像拼接在一起，左边显示原视频，右边显示校正视频
        cv2.imshow('left_ori,right_correction', compare)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    distortion_correction_cam()

