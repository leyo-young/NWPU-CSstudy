# region 库文件
import ctypes
import inspect
import re
import threading
import time
import cv2
import numpy as np
from detect_main import *
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QRegExpValidator, QIntValidator, QPixmap
from MainWindow import Ui_MainWindow
import sys
from PyQt5.QtWidgets import *
from Five_Robot_Control import *
from PyQt5 import QtCore, QtGui, QtWidgets
from calibration import *
from Five_Robot_kinematics import *
# endregion
# region全局变量
global image  # 相机图像
global shap_count_circles#圆形计数
shap_count_circles=0
global shape_count_square#正方形计数
shape_count_square=0
global result #检测结果
result=[]
global bool_IsSend
bool_IsSend=False
global clip_open_degree#夹爪每次放置物体时张开夹爪度数，防止夹爪张开过大碰撞到其它
clip_open_degree=40
global clip_close_degree#夹爪关闭时角度
clip_close_degree=70
# endregion
# region 实例化对象
robot_control = Five_Robot_Control()
calibration=Cam_Calibration()
five_robot_kinematics=Five_Robot_kinematics()
object_recognition = my_nanodet()
# endregion
# region 机械臂示教和运动控制
class Five_Robot_Arm(QMainWindow, Ui_MainWindow):
    # region 构造函数
    def __init__(self):  # 创建构造函数
        super().__init__()  # 调用父类函数，继承
        self.setupUi(self)  # 调用UI
        self.btn_ini(False)  # 控制相关按钮不使能
        self.btn_enable_on.setEnabled(False)
        self.btn_enable_off.setEnabled(False)
        # self.btn_close_detection.setEnabled(False)
        #限制line_Edit的输入只能是数字
        self.lineEdit_step.setValidator(QIntValidator(1,240))#只能输入1-240数字
        self.lineEdit_speed.setValidator(QRegExpValidator(QRegExp("[0-9]+$")))#只能输入数字
        #图像显示相关操作
        self.timer_camera = QtCore.QTimer()  # 定时器
        self.cap = cv2.VideoCapture(0)  # 准备获取图像
        ret, image = self.cap.read()
        if ret != True:
            self.CAM_NUM = 3 #由于系统初始化USB口是随机顺序,USB相机的端口号可能是0或者3
        else:
            self.CAM_NUM = 0
        #发送数据，机器人执行抓取线程
        self.thread_send = threading.Thread(target=self.send_data)
        self.thread_send.start()
        #显示→打开相机
        self.button_open_camera_click()
        self.slot_init()  # 设置槽函数
    # endregion
    # region 设置槽函数
    def slot_init(self):
        # 复位按钮
        self.btn_reduce.clicked.connect(self.btn_reduce_click)
        # 归零按钮
        self.btn_zero.clicked.connect(self.btn_zero_click)
        # 启动按钮
        self.btn_start.clicked.connect(self.btn_start_click)
        # 关节1：加,减
        self.btn_j1_add.clicked.connect(self.btn_j1_add_click)
        self.btn_j1_subtract.clicked.connect(self.btn_j1_subtract_click)
        # 关节2：加,减
        self.btn_j2_add.clicked.connect(self.btn_j2_add_click)
        self.btn_j2_subtract.clicked.connect(self.btn_j2_subtract_click)
        # 关节3：加,减
        self.btn_j3_add.clicked.connect(self.btn_j3_add_click)
        self.btn_j3_subtract.clicked.connect(self.btn_j3_subtract_click)
        # 关节4：加,减
        self.btn_j4_add.clicked.connect(self.btn_j4_add_click)
        self.btn_j4_subtract.clicked.connect(self.btn_j4_subtract_click)
        # 夹爪开/关
        self.btn_clip_open.clicked.connect(self.btn_clip_open_click)
        self.btn_clip_close.clicked.connect(self.btn_clip_close_click)
        # 步长按钮
        self.btn_step_1.clicked.connect(self.btn_step_1_click)
        self.btn_step_5.clicked.connect(self.btn_step_5_click)
        self.btn_step_10.clicked.connect(self.btn_step_10_click)
        self.btn_step_15.clicked.connect(self.btn_step_15_click)
        # 速度按钮
        self.btn_speed_30.clicked.connect(self.btn_speed_30_click)
        self.btn_speed_100.clicked.connect(self.btn_speed_100_click)
        # 使能按钮
        self.btn_enable_on.clicked.connect(self.btn_enable_on_click)
        self.btn_enable_off.clicked.connect(self.btn_enable_off_click)
        #视觉相关
        self.btn_open_detection.clicked.connect(self.btn_open_detection_click)
        self.btn_close_detection.clicked.connect(self.btn_close_detection_click)
        self.timer_camera.timeout.connect(self.show_camera)

    # endregion
    # region 启动按钮初始化
    # 控制部分按钮是否使能
    def btn_ini(self, bool):
        self.btn_zero.setEnabled(bool)
        self.btn_j1_add.setEnabled(bool)
        self.btn_j1_subtract.setEnabled(bool)
        self.btn_j2_add.setEnabled(bool)
        self.btn_j2_subtract.setEnabled(bool)
        self.btn_j3_add.setEnabled(bool)
        self.btn_j3_subtract.setEnabled(bool)
        self.btn_j4_add.setEnabled(bool)
        self.btn_j4_subtract.setEnabled(bool)
        self.btn_step_1.setEnabled(bool)
        self.btn_step_5.setEnabled(bool)
        self.btn_step_10.setEnabled(bool)
        self.btn_step_15.setEnabled(bool)
        self.lineEdit_step.setEnabled(bool)
        self.btn_speed_30.setEnabled(bool)
        self.btn_speed_100.setEnabled(bool)
        self.lineEdit_speed.setEnabled(bool)
        self.btn_clip_open.setEnabled(bool)
        self.btn_clip_close.setEnabled(bool)
        self.btn_open_detection.setEnabled(bool)
        self.btn_close_detection.setEnabled(bool)
    # endregion
    # region 使能按钮
    def btn_enable_on_click(self):
        self.btn_ini(True)
        robot_control.bus_servo_niuju_on(0xfe)
        degree = robot_control.bus_servo_get_all()
        if degree[0] <= 260:
            self.btn_enable_on.setStyleSheet("QPushButton {text-align : center;\n"
                                             "             background-color : green;\n"
                                             "             font: bold;\n"
                                             "             border-color: gray;\n"
                                             "             border-width: 2px;\n"
                                             "             border-radius: 15px;\n"
                                             "             padding: 6px;\n"
                                             "             height : 14px;\n"
                                             "             border-style: outset;\n"
                                             "             font : 14px;}\n")
            self.btn_enable_off.setStyleSheet("QPushButton {text-align : center;\n"
                                              "             background-color : rgb(216,216,216);\n"
                                              "             font: bold;\n"
                                              "             border-color: gray;\n"
                                              "             border-width: 2px;\n"
                                              "             border-radius: 15px;\n"
                                              "             padding: 6px;\n"
                                              "             height : 14px;\n"
                                              "             border-style: outset;\n"
                                              "             font : 14px;}\n")
            self.label_j1.setText(str(degree[0]))
            self.label_j2.setText(str(degree[1]))
            self.label_j3.setText(str(degree[2]))
            self.label_j4.setText(str(degree[3]))
            print("夹爪:",degree[4])

    def btn_enable_off_click(self):
        self.btn_ini(False)  # 使能关闭，所有的先关操作不使能
        self.btn_enable_on.setStyleSheet("QPushButton {text-align : center;\n"
                                         "             background-color : rgb(216，216，216);\n"
                                         "             font: bold;\n"
                                         "             border-color: gray;\n"
                                         "             border-width: 2px;\n"
                                         "             border-radius: 15px;\n"
                                         "             padding: 6px;\n"
                                         "             height : 14px;\n"
                                         "             border-style: outset;\n"
                                         "             font : 14px;}\n")
        self.btn_enable_off.setStyleSheet("QPushButton {text-align : center;\n"
                                          "             background-color : red;\n"
                                          "             font: bold;\n"
                                          "             border-color: gray;\n"
                                          "             border-width: 2px;\n"
                                          "             border-radius: 15px;\n"
                                          "             padding: 6px;\n"
                                          "             height : 14px;\n"
                                          "             border-style: outset;\n"
                                          "             font : 14px;}\n")
        robot_control.bus_servo_niuju_off(0xfe)

    # endregion
    # region 复位按钮点击事件
    def btn_reduce_click(self):
        self.btn_ini(False)
        self.btn_enable_on.setEnabled(False)
        self.btn_enable_off.setEnabled(False)
        robot_control.bus_pwr_off()
        self.btn_enable_on.setStyleSheet("QPushButton {text-align : center;\n"
                                         "             background-color : rgb(216，216，216);\n"
                                         "             font: bold;\n"
                                         "             border-color: gray;\n"
                                         "             border-width: 2px;\n"
                                         "             border-radius: 15px;\n"
                                         "             padding: 6px;\n"
                                         "             height : 14px;\n"
                                         "             border-style: outset;\n"
                                         "             font : 14px;}\n")
        self.btn_enable_off.setStyleSheet("QPushButton {text-align : center;\n"
                                          "             background-color : red;\n"
                                          "             font: bold;\n"
                                          "             border-color: gray;\n"
                                          "             border-width: 2px;\n"
                                          "             border-radius: 15px;\n"
                                          "             padding: 6px;\n"
                                          "             height : 14px;\n"
                                          "             border-style: outset;\n"
                                          "             font : 14px;}\n")

    # endregion
    # region 归零按钮事件
    def btn_zero_click(self):
        wait_point = [30, 45, 182, 219, 0, 2000]
        robot_control.bus_servo_all(wait_point[0], wait_point[1], wait_point[2], wait_point[3], wait_point[4],
                                    wait_point[5])
        self.label_j1.setText(str(wait_point[0]))
        self.label_j2.setText(str(wait_point[1]))
        self.label_j3.setText(str(wait_point[2]))
        self.label_j4.setText(str(wait_point[3]))

    # endregion
    # region 启动按钮
    def btn_start_click(self):
        robot_control.bus_servo_pwr_on()
        self.btn_enable_on.setEnabled(True)
        self.btn_enable_off.setEnabled(True)

    # endregion
    # region  关节控制
    def btn_j1_add_click(self):
        degree = int(self.label_j1.text()) + int(self.lineEdit_step.text())
        if degree <= 240:
            robot_control.bus_servo(1, degree, int(self.lineEdit_speed.text()))
            self.label_j1.setText(str(degree))

    def btn_j1_subtract_click(self):
        degree = int(self.label_j1.text()) - int(self.lineEdit_step.text())
        if degree >= 0:
            robot_control.bus_servo(1, degree, int(self.lineEdit_speed.text()))
            self.label_j1.setText(str(degree))

    def btn_j2_add_click(self):
        degree = int(self.label_j2.text()) + int(self.lineEdit_step.text())
        if degree <= 216:
            robot_control.bus_servo(2, degree, int(self.lineEdit_speed.text()))
            self.label_j2.setText(str(degree))

    def btn_j2_subtract_click(self):
        degree = int(self.label_j2.text()) - int(self.lineEdit_step.text())
        if degree >= 24:
            robot_control.bus_servo(2, degree, int(self.lineEdit_speed.text()))
            self.label_j2.setText(str(degree))

    def btn_j3_add_click(self):
        degree = int(self.label_j3.text()) + int(self.lineEdit_step.text())
        if degree <= 240:
            robot_control.bus_servo(3, degree, int(self.lineEdit_speed.text()))
            self.label_j3.setText(str(degree))

    def btn_j3_subtract_click(self):
        degree = int(self.label_j3.text()) - int(self.lineEdit_step.text())
        if degree >= 16:
            robot_control.bus_servo(3, degree, int(self.lineEdit_speed.text()))
            self.label_j3.setText(str(degree))

    def btn_j4_add_click(self):
        degree = int(self.label_j4.text()) + int(self.lineEdit_step.text())
        if degree <= 240:
            robot_control.bus_servo(4, degree, int(self.lineEdit_speed.text()))
            self.label_j4.setText(str(degree))

    def btn_j4_subtract_click(self):
        degree = int(self.label_j4.text()) - int(self.lineEdit_step.text())
        if degree >= 10:
            robot_control.bus_servo(4, degree, int(self.lineEdit_speed.text()))
            self.label_j4.setText(str(degree))

    def btn_clip_open_click(self):
        robot_control.bus_servo(5, 0, int(self.lineEdit_speed.text()))

    def btn_clip_close_click(self):
        robot_control.bus_servo(5, 100, int(self.lineEdit_speed.text()))

    def btn_step_1_click(self):
        self.lineEdit_step.setText('1')

    def btn_step_5_click(self):
        self.lineEdit_step.setText('5')

    def btn_step_10_click(self):
        self.lineEdit_step.setText('10')

    def btn_step_15_click(self):
        self.lineEdit_step.setText('15')

    def btn_speed_30_click(self):
        self.lineEdit_speed.setText('30')

    def btn_speed_100_click(self):
        self.lineEdit_speed.setText('100')

    # endregion
    #region 判断字符串是否是数值类型
    def is_number(self,s):
        try:
            int(s)
            return True
        except Exception as e:
            print("数值转换整型错误:",e)
            pass
        try:
            import unicodedata
            unicodedata.numeric(s)
        except Exception as e:
            print("数值转换整型错误:", e)
        return False
    #endregion
    #region 视觉处理
    # 定时器事件函数
    def button_open_camera_click(self):
        if self.timer_camera.isActive() == False:
            flag = self.cap.open(self.CAM_NUM)
            if flag == False:
                msg = QtWidgets.QMessageBox.warning(
                    self, u"Warning", u"请检测相机与电脑是否连接正确",
                    buttons=QtWidgets.QMessageBox.Ok,
                    defaultButton=QtWidgets.QMessageBox.Ok)
            else:
                self.timer_camera.start(30)
    # 显示图像
    def show_camera(self):
        global image
        flag, self.image = self.cap.read()
        show = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)  # 图像格式转为RGB
        showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format_RGB888)  # 设置显示格式
        self.Image_show.setPixmap(QtGui.QPixmap.fromImage(showImage))  # 显示图像
        self.Image_show.setScaledContents(True)  # 图像自适应窗口大小
    #开始检测
    def btn_open_detection_click(self):
        try:
            self.btn_open_detection.setEnabled(False)
            self.btn_close_detection.setEnabled(False)
            self.btn_ini(False)
            global image
            self.timer_camera.stop()
            global result
            result = []
            img, result= object_recognition.detect(self.image)#颜色形状识别
            print(result)
            self.Image_show.setPixmap(QPixmap(''))
            show = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # 图像格式转为RGB
            showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format_RGB888)  # 设置显示格式
            self.Image_show.setPixmap(QtGui.QPixmap.fromImage(showImage))  # 显示图像
            self.Image_show.setScaledContents(True)  # 图像自适应窗口大小
            global bool_IsSend
            if self.cbx_Ispick.isChecked():
                bool_IsSend=True
            else:
                bool_IsSend = False
                self.btn_close_detection.setEnabled(True)
        except Exception as e:
            print("数据获取失败：", e)
            self.btn_close_detection.setEnabled(True)
    #发送数据，机器人执行抓取
    def send_data(self):
        try:
            while True:
                time.sleep(0.1)
                global bool_IsSend
                if bool_IsSend==True:
                    bool_IsSend = False
                    global result
                    self.robot_pick(int(result[0]), int(result[1]))  # 抓取
                    self.btn_close_detection.setEnabled(True)#抓取完毕后使能关闭检测，开启采集定时器
                    # result=[]
        except Exception as e:
            print("数据发送线程：", e)
    #关闭检测
    def btn_close_detection_click(self):
        self.btn_ini(True)
        degree = robot_control.bus_servo_get_all()
        if degree[0] <= 260:
            self.label_j1.setText(str(degree[0]))
            self.label_j2.setText(str(degree[1]))
            self.label_j3.setText(str(degree[2]))
            self.label_j4.setText(str(degree[3]))
        self.btn_open_detection.setEnabled(True)
        self.btn_close_detection.setEnabled(False)
        self.timer_camera.start(30)
    #endregion
    #region 机械臂抓取，物体分类
    def robot_pick(self,pixel_x, pixel_y):
        point_x, point_y = calibration.calibration(pixel_x, pixel_y)  # 像素坐标得到世界坐标
        print("x,y:", point_x, point_y)
        arr1, arr2, arr3, arr4 = five_robot_kinematics.arr(point_x, point_y, 0)  # 最后一个为Z轴，输出四个角度
        print(arr1, arr2, arr3, arr4)
        robot_control.bus_servo_niuju_on(0xfe)
        time.sleep(0.5)
        robot_control.bus_servo_all(30, 58, 170, 217, 0, 1000)
        time.sleep(2)
        robot_control.bus_servo_all(arr1, arr2, arr3, arr4, 0, 1000)
        time.sleep(2)
        robot_control.bus_servo_all(arr1, arr2, arr3, arr4, clip_close_degree, 1000)
        time.sleep(2)
        robot_control.bus_servo_all(30, 74, 172, 198, clip_close_degree, 1000)
        time.sleep(2)
        robot_control.bus_servo_all(200, 74, 172, 198, clip_close_degree, 1000)
        time.sleep(2)
        global result
        self.object_classify(result[2])
        robot_control.bus_servo_all(200, 74, 172, 198, 0, 1000)
        time.sleep(2)
        robot_control.bus_servo_all(30, 58, 170, 217, 0, 1000)
        # result=[]
    def object_classify(self,fruit):
        global clip_open_degree
        global clip_close_degree
        point1_place = [213, 96, 193, 204,clip_close_degree,1000]#示教四个摆放位置依次是1234，颜色按照红蓝黄绿，如果形状相同按照左右排列
        point2_place = [192, 96, 193, 204,clip_close_degree,1000]
        point3_place = [220, 47, 210, 227,clip_close_degree,1000]
        point4_place = [185, 47, 210, 227,clip_close_degree,1000]
        #选择颜色分类，红蓝黄绿排列
        if self.cbx_Ispick_shape.isChecked()==True:
            if fruit=="banana":
                 robot_control.bus_servo_all(point1_place[0], point1_place[1], point1_place[2], point1_place[3], point1_place[4], point1_place[5])
                 time.sleep(1)
                 robot_control.bus_servo_all(point1_place[0], point1_place[1], point1_place[2], point1_place[3],clip_close_degree-clip_open_degree, point1_place[5])
                 time.sleep(1)
                 robot_control.bus_servo_all(point1_place[0], point1_place[1], point1_place[2], 207,clip_close_degree - clip_open_degree, point1_place[5])
                 time.sleep(1)
            elif fruit=="tomato":
                robot_control.bus_servo_all(point2_place[0], point2_place[1], point2_place[2], point2_place[3],
                                            point2_place[4], point2_place[5])
                time.sleep(1)
                robot_control.bus_servo_all(point2_place[0], point2_place[1], point2_place[2], point2_place[3],
                                            clip_close_degree - clip_open_degree, point2_place[5])
                time.sleep(1)
                robot_control.bus_servo_all(point2_place[0], point2_place[1], point2_place[2], 207,
                                            clip_close_degree - clip_open_degree, point2_place[5])
                time.sleep(1)
            elif fruit=="watermelon":
                robot_control.bus_servo_all(point3_place[0], point3_place[1], point3_place[2], point3_place[3],
                                            point3_place[4], point3_place[5])
                time.sleep(1)
                robot_control.bus_servo_all(point3_place[0], point3_place[1], point3_place[2], point3_place[3],
                                            clip_close_degree - clip_open_degree, point3_place[5])
                time.sleep(1)
                robot_control.bus_servo_all(point3_place[0], point3_place[1], point3_place[2], 207,
                                            clip_close_degree - clip_open_degree, point3_place[5])
                time.sleep(1)
            elif fruit=="cucumber":
                robot_control.bus_servo_all(point4_place[0], point4_place[1], point4_place[2], point4_place[3],
                                            point4_place[4], point4_place[5])
                time.sleep(1)
                robot_control.bus_servo_all(point4_place[0], point4_place[1], point4_place[2], point4_place[3],
                                            clip_close_degree - clip_open_degree, point4_place[5])
                time.sleep(1)
                robot_control.bus_servo_all(point4_place[0], point4_place[1], point4_place[2], 207,
                                            clip_close_degree - clip_open_degree, point4_place[5])
                time.sleep(1)
            else:
                return

    # endregion
    # region退出程序，关闭线程
    def closeEvent(self, event):
        if self.timer_camera.isActive() != False:
                if self.cap.isOpened():
                    self.cap.release()
                if self.timer_camera.isActive():
                    self.timer_camera.stop()
        self.stop_thread(self.thread_send)  # 关闭线程
        self.close()
    def _async_raise(self, tid, exctype):
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")
    def stop_thread(self, thread):
        self._async_raise(thread.ident, SystemExit)
    # endregion

# region 主程序运行
if __name__ == "__main__":
    app = QApplication(sys.argv)
    five_robot = Five_Robot_Arm()
    five_robot.show()
    sys.exit(app.exec_())
# endregion
# endregion

