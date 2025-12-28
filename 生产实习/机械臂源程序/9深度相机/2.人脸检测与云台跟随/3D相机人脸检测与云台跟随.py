# from PyQt5.QtWidgets import QApplication,QMainWindow
import sys
from mainui import Ui_MainWindow
import cv2
import time
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
import serial

data_ser = serial.Serial("/dev/user_robot", 115200, timeout=5)  # 云台接收的串口，设备波特率为115200
global value,x
value = 90
class Mywindow(QMainWindow, Ui_MainWindow):
    def __init__(self):  # 创建构造函数
        super().__init__()  # 调用父类函数，继承
        self.timer_camera = QtCore.QTimer()  # 定时器
        # 数据帧
        self.setupUi(self)  # 调用UI
        self.cap = cv2.VideoCapture(2)  # 准备获取图像
        ret,image=self.cap.read()
        if ret!=True:
            self.CAM_NUM = 3
        else:
            self.CAM_NUM = 2
        self.slot_init()  # 设置槽函数

    def slot_init(self):
        # 设置槽函数
        self.pushButton_open.clicked.connect(self.button_open_camera_click)
        self.timer_camera.timeout.connect(self.face_detect_demo)
        self.pushButton_close.clicked.connect(self.closeEvent)

    # 开启采集定时器
    def button_open_camera_click(self):
        self.bus_bjdj(0x5A)  # 使云台抬升
        if self.timer_camera.isActive() == False:
            flag = self.cap.open(self.CAM_NUM)
            if flag == False:
                msg = QtWidgets.QMessageBox.warning(
                    self, u"Warning", u"请检测相机与电脑是否连接正确",
                    buttons=QtWidgets.QMessageBox.Ok,
                    defaultButton=QtWidgets.QMessageBox.Ok)
            else:
                self.timer_camera.start(10)

    # 关闭相机显示
    def closeEvent(self):
        if self.timer_camera.isActive() != False:
            ok = QtWidgets.QPushButton()
            cacel = QtWidgets.QPushButton()
            msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, u"关闭", u"是否关闭！")
            msg.addButton(ok, QtWidgets.QMessageBox.ActionRole)
            msg.addButton(cacel, QtWidgets.QMessageBox.RejectRole)
            ok.setText(u'确定')
            cacel.setText(u'取消')
            if msg.exec_() != QtWidgets.QMessageBox.RejectRole:
                if self.cap.isOpened():
                    self.cap.release()
                if self.timer_camera.isActive():
                    self.timer_camera.stop()
                self.label_imput_image.setText(
                    "<html><head/><body><p align=\"center\"><img src=\":/newPrefix/pic/Hint.png\"/><span style=\" font-size:28pt;\">点击打开云台跟踪</span><br/></p></body></html>")

    # 人脸检测
    def face_detect_demo(self):
        flag, self.image = self.cap.read()
        self.image = cv2.flip(self.image, 1)  # 左右翻转
        imageshow = self.image.copy()
        imageshow = cv2.cvtColor(imageshow, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        face_detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        faces = face_detector.detectMultiScale(gray, 1.1, 5)
        global value,x
        for x, y, w, h in faces:
            cv2.rectangle(imageshow, (x, y), (x + w, y + h), (0, 0, 255), 2)
            print("x:",x+w/2)
            if x+w/2 >= 0 and x+w/2 <= 270:
                value = value - 1
                if value <= 20:
                    value = 20
            if x+w/2 >= 380 and x+w/2 <= 640:
                value = value + 1
                if value >= 160:
                    value = 160
            print("value:",value)
        self.bus_bjdj(int(value))
        recImage = QtGui.QImage(imageshow.data, imageshow.shape[1], imageshow.shape[0], QtGui.QImage.Format_RGB888)
        self.label_imput_image.setPixmap(QtGui.QPixmap.fromImage(recImage))
        self.label_imput_image.setScaledContents(True)

    # 控制云台转动
    def bus_bjdj(self, value):  # 步进电机位置控制（id，位置）0-315mm
        ddata = [0xFF, 0xFE, 0x02, 0x01, 0x00, 0x01, 0x46, 0x00, 0x0D, 0x0A]
        ddata[5] = value
        data_ser.write(ddata)  # 串口发送数据
        time.sleep(0.1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mywindow = Mywindow()
    mywindow.show()
    app.exec_()
