import sys
import numpy as np
import cv2
import serial
import time

data_ser = serial.Serial("/dev/user_robot", 115200, timeout=5)  # 云台接收的串口，设备波特率为115200
modelFile = "opencv_face_detector_uint8.pb"#包含实际权重训练模型文件
configFile = "opencv_face_detector.pbtxt"#定义模型结构配置文件
net = cv2.dnn.readNetFromTensorflow(modelFile, configFile)#加载检测模型数据
conf_threshold = 0.7#人脸检测可信度

# 控制云台转动
def bus_bjdj( value):  # 步进电机位置控制（id，位置）0-315mm
    ddata = [0xFF, 0xFE, 0x02, 0x01, 0x00, 0x01, 0x46, 0x00, 0x0D, 0x0A]
    ddata[5] = value
    data_ser.write(ddata)  # 串口发送数据
    time.sleep(0.1)
# 人脸检测：前面人脸识别采用的也是opencvDNN检测模型检测人脸，这里检测效果好是因为对人脸模型进行了优化，前者是opencv自带的检测模型
def detectFaceOpenCVDnn(net, frame):
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), [104, 117, 123], False, False)#创建图像的块数据，blobFromImage主要是用来对图片进行预处理，整体像素值减去平均值，通过缩放系数对图片像素值进行缩放
    frameHeight = frame.shape[0]#获得图像尺寸
    frameWidth = frame.shape[1]
    net.setInput(blob)#将块数据设置为输入
    list_box = []
    detections = net.forward()#执行计算，获得检测结果
    for i in range(detections.shape[2]):#迭代，输出可信度高的人脸检测结果
        confidence = detections[0, 0, i, 2]#获得可信度
        if confidence > conf_threshold:#输出可信度高于70%的结果
            x1 = int(detections[0, 0, i, 3] * frameWidth)
            y1 = int(detections[0, 0, i, 4] * frameHeight)
            x2 = int(detections[0, 0, i, 5] * frameWidth)
            y2 = int(detections[0, 0, i, 6] * frameHeight)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)   #获得人脸在图像中的坐标
            list_box.append((x1, y1, x2, y2))
            y = y1 - 10 if y1 - 10 > 10 else y1 + 10  # 计算可信度输出位置
            text = "%.3f" % (confidence * 100) + '%'
            cv2.putText(frame, text, (x1, y-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 1)  # 输出可信度
    if len(list_box) > 0:
        return True, list_box#返回检测到人脸数据数组
    return False, list_box
#判断是否有口罩，根据检测到人脸图像的HSV图像轮廓与整张图的大小的比例关系来判断有无带口罩
def If_Have_Mask(x1, y1, x2, y2):
    try:
        img = image[y1:y2, x1:x2].copy()#原图中取人脸ROI区域
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)#人脸图转灰度
        lower_hsv_1 = np.array([0, 30, 30])  # 颜色范围低阈值
        upper_hsv_1 = np.array([40, 255, 255])  # 颜色范围高阈值
        lower_hsv_2 = np.array([140, 30, 30])  # 颜色范围低阈值
        upper_hsv_2 = np.array([180, 255, 255])  # 颜色范围高阈值
        mask1 = cv2.inRange(hsv_img, lower_hsv_1, upper_hsv_1)#根据阈值取掩模
        mask2 = cv2.inRange(hsv_img, lower_hsv_2, upper_hsv_2)
        mask = mask1 + mask2
        mask = cv2.GaussianBlur(mask, (15, 15), 1)#高斯滤波
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)#找轮廓
        if len(contours) < 1:
            return "No Mask"
        area = []
        for k in range(len(contours)):#获取最大面积的轮廓
            area.append(cv2.contourArea(contours[k]))
        max_idx = np.argmax(np.array(area))
        mask_rate = area[max_idx] / (img.shape[0] * img.shape[1])#求最大轮廓与图像的比例
        if mask_rate < 0.65:
            cv2.putText(image, "Have Mask", (x1 + int((x2 - x1) / 2) - 50, y1 - 10), cv2.FONT_HERSHEY_COMPLEX, 0.7,
                        (0, 0, 255), 2)
        else:
            cv2.putText(image, "No Mask", (x1 + int((x2 - x1) / 2) - 50, y1 - 10), cv2.FONT_HERSHEY_COMPLEX, 0.7,
                        (0, 0, 255), 2)
    except:
        return
if __name__ == '__main__':
    bus_bjdj(0x5A)  # 使云台抬升
    cam = cv2.VideoCapture(2)#采集图像
    ret,image=cam.read()
    if ret!=True:
        cam = cv2.VideoCapture(3)  # 采集图像
    while True:
        ret, image = cam.read()
        if ret == True:
            nRes, list_box = detectFaceOpenCVDnn(net, image)#检测人脸，返回人脸检测数组
            if nRes == True:
                for _box in list_box:
                    x1, y1, x2, y2 = _box
                    If_Have_Mask(x1, y1, x2, y2)#判断口罩有无
            cv2.imshow("face_detection", image)
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
        else:
            print("相机没打开")
    cam.release()
    cv2.destroyAllWindows()
