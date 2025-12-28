import pyrealsense2 as rs
import numpy as np
import cv2
import time
import serial
import random

data_ser = serial.Serial("/dev/user_robot", 115200, timeout=5)  # 云台串口，设备波特率为115200
global object_x#检测物体中心点X的坐标
global object_y#检测物体中心点Y的坐标
#云台控制
def bus_bjdj(value):  # 步进电机位置控制（id，位置）0-315mm
    ddata = [0xFF,0xFE,0x02,0x01,0x00, 0x01, 0x46,0x00,0x0D,0x0A]
    ddata[5] = value
    data_ser.write(ddata)#串口发送数据
    time.sleep(0.1)
if __name__ == '__main__':
    bus_bjdj(0x5A)#控制云台抬起摄像头
    pipeline = rs.pipeline()  # 创建一个管道
    config = rs.config()  # Create a config并配置要流式传输的管道。
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)#使用选定的流参数
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    # Start streaming 开启流
    pipeline.start(config)
    align = rs.align(rs.stream.color) #深度图像向彩色对齐
    print(type(align))
    global object_x
    global object_y
    object_x = 320  # 修改成检测目标的中心点即可
    object_y = 240
    try:
        while True:
            frames = pipeline.wait_for_frames()  # 等待开启通道
            aligned_frames = align.process(frames)  # 将深度框和颜色框对齐
            depth_frame = aligned_frames.get_depth_frame()  # 获得对齐后的帧数深度数据(图)
            color_frame = aligned_frames.get_color_frame()  # 获得对齐后的帧数颜色数据(图)
            img_color = np.asanyarray(color_frame.get_data())  # 把图像像素转化为数组
            img_depth = np.asanyarray(depth_frame.get_data())  # 把图像像素转化为数组
            # Apply colormap on depth image (image must be converted to 8-bit per pixel first) 在深度图上用颜色渲染
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(img_depth, alpha=0.03), cv2.COLORMAP_JET)
            #人脸检测中点
            image = img_color.copy()
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)#转灰度
            face_detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")#加载人脸检测模型数据
            faces = face_detector.detectMultiScale(gray, 1.1, 5)#检测人脸
            for x, y, w, h in faces:
                cv2.rectangle(img_color, (x, y), (x + w, y + h), (0, 0, 255), 2)#根据检测的数据画矩形框
                object_x=round(x+w/2)
                object_y=round(y+h/2)
                print("object_x:",object_x)
                print("object_y:", object_y)
                # 获取目标框内的物体距离，并进行均值滤波
                depth_points = []
                for j in range(50):#取50个点的随机数测量平均深度值
                    rand_x = random.randint(x, x + w)
                    rand_y = random.randint(y, y + h)
                    depth_point = round(depth_frame.get_distance(rand_x, rand_y)*1000, 2)
                    if depth_point != 0:
                        depth_points.append(depth_point)
                depth_object = np.mean(depth_points)
                if depth_object >= 300:
                    print("The camera is facing an object mean ", int(depth_object), " mm away.")
                else:
                    print("The camera is facing an object mean <300 mm away.")
                cv2.circle(img_color, (int(object_x), int(object_y)), 8, [0, 0, 255], thickness=-1)#画出中心点
                cv2.putText(img_color, "Distance:" + str(round(depth_object)) + "mm", (5, 40),cv2.FONT_HERSHEY_SIMPLEX, 0.5, [255, 0, 255])#写出距离值
            image_new = np.hstack((depth_colormap,img_color ))#图像拼接在一起
            cv2.imshow("RealSense:",image_new)
            key = cv2.waitKey(10)
            if key & 0xFF == ord('q') or key == 27:
                cv2.destroyAllWindows()
                break
    finally:
        pipeline.stop()#关闭流
