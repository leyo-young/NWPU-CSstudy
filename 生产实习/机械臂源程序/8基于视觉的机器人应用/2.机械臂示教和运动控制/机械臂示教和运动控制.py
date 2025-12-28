# region 库文件
import ctypes
import inspect
import re
import threading
import time
import numpy as np
from tkinter import filedialog
import tkinter
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QRegExpValidator, QIntValidator
from MainWindows import Ui_MainWindow
import sys
from PyQt5.QtWidgets import *
from Five_Robot_Control import *

# endregion
# region 机器人控制实例化对象
robot_control = Five_Robot_Control()
# endregion
# region全局变量
global item  # 保存tableview所有行数据
item = []
global isRunStop  # 程序运行是否停止标志位
isRunStop = True


# endregion
# region 机械臂示教和运动控制
class Five_Robot_Arm(QMainWindow, Ui_MainWindow):
    # region 构造函数
    def __init__(self):  # 创建构造函数
        super().__init__()  # 调用父类函数，继承
        self.setupUi(self)  # 调用UI
        # 函数调用 初始化 tableView
        self.tableView_init()
        self.slot_init()  # 设置槽函数
        self.btn_ini(False)  # 控制相关按钮不使能
        self.btn_ini_1(False)  # 程序运行相关按钮不使能
        self.btn_enable_on.setEnabled(False)
        self.btn_enable_off.setEnabled(False)
        # 获取到item后开启发送线程
        self.thread_run_stop = threading.Thread(target=self.send_robot_data)
        self.thread_run_stop.start()
        # 设置背景显示文本
        self.lineEdit_file_name.setPlaceholderText("输入程序名称")
        #限制line_Edit的输入只能是数字
        self.lineEdit_recur.setValidator(QRegExpValidator(QRegExp("[0-9]+$")))#只能输入数字
        self.lineEdit_step.setValidator(QIntValidator(1,240))#只能输入1-240数字
        self.lineEdit_speed.setValidator(QRegExpValidator(QRegExp("[0-9]+$")))#只能输入数字


    # endregion
    # region 设置槽函数
    def slot_init(self):
        # 添加按钮
        self.btn_add.clicked.connect(self.btn_add_click)
        # 插入按钮
        self.btn_insert.clicked.connect(self.btn_insert_click)
        # 删除单行按钮
        self.btn_del.clicked.connect(self.btn_del_click)
        # 清除所有行按钮
        self.btn_clear.clicked.connect(self.btn_clear_click)
        # 上移按钮
        self.btn_move_up.clicked.connect(self.btn_move_up_click)
        # 下移按钮
        self.btn_move_down.clicked.connect(self.btn_move_down_click)
        # 复制按钮
        self.btn_copy.clicked.connect(self.btn_copy_click)
        # 粘贴按钮
        self.btn_stick.clicked.connect(self.btn_stick_click)
        # 运行程序按钮
        self.btn_run.clicked.connect(self.btn_run_click)
        # 运行停止按钮
        self.btn_stop.clicked.connect(self.btn_stop_click)
        # 单步运行按钮
        self.btn_step.clicked.connect(self.btn_step_click)
        # 更新按钮
        self.btn_renew.clicked.connect(self.btn_renew_click)
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
        # 程序保存
        self.btn_save_file.clicked.connect(self.btn_save_file_click)
        # 打开程序
        self.btn_open_file.clicked.connect(self.btn_open_file_click)
        # 拖动示教
        self.btn_teach_on.clicked.connect(self.btn_teach_on_click)
        self.btn_teach_off.clicked.connect(self.btn_teach_off_click)

    # endregion
    # region 启动按钮初始化
    # 控制部分按钮是否使能
    def btn_ini(self, bool):
        self.btn_teach_on.setEnabled(bool)
        self.btn_teach_off.setEnabled(bool)
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

    # 程序操作部分是否使能
    def btn_ini_1(self, bool):
        self.btn_open_file.setEnabled(bool)
        self.btn_save_file.setEnabled(bool)
        self.lineEdit_file_name.setEnabled(bool)
        self.lineEdit_recur.setEnabled(bool)
        self.btn_run.setEnabled(bool)
        self.btn_stop.setEnabled(bool)
        self.btn_step.setEnabled(bool)
        self.btn_add.setEnabled(bool)
        self.btn_insert.setEnabled(bool)
        self.btn_renew.setEnabled(bool)
        self.btn_move_up.setEnabled(bool)
        self.btn_move_down.setEnabled(bool)
        self.btn_stick.setEnabled(bool)
        self.btn_copy.setEnabled(bool)
        self.btn_del.setEnabled(bool)
        self.btn_clear.setEnabled(bool)

    # 程序操作部分是否使能排除停止按钮
    def btn_ini_2(self, bool):
        self.btn_open_file.setEnabled(bool)
        self.btn_save_file.setEnabled(bool)
        self.lineEdit_file_name.setEnabled(bool)
        self.lineEdit_recur.setEnabled(bool)
        self.btn_run.setEnabled(bool)
        self.btn_step.setEnabled(bool)
        self.btn_add.setEnabled(bool)
        self.btn_insert.setEnabled(bool)
        self.btn_renew.setEnabled(bool)
        self.btn_move_up.setEnabled(bool)
        self.btn_move_down.setEnabled(bool)
        self.btn_stick.setEnabled(bool)
        self.btn_copy.setEnabled(bool)
        self.btn_del.setEnabled(bool)
        self.btn_clear.setEnabled(bool)
        self.tableView.setEnabled(bool)

    # endregion
    # region 拖动示教
    def btn_teach_on_click(self):
        robot_control.bus_servo_niuju_off(0xfe)  # 关闭使能
        self.btn_teach_on.setEnabled(False)  # 点击拖动示教后开启线程就不能再点击
        self.btn_teach_off.setEnabled(True)
        self.btn_enable_on.setEnabled(False)
        self.btn_enable_off.setEnabled(False)
        self.btn_ini_1(True)
        self.btn_ini(False)#拖动示教打开，控制不能操作
        self.btn_teach_off.setEnabled(True)#拖动示教关闭可用
        self.btn_teach_on.setStyleSheet("QPushButton {text-align : center;\n"
                                        "             background-color : green;\n"
                                        "             font: bold;\n"
                                        "             border-color: gray;\n"
                                        "             border-width: 2px;\n"
                                        "             border-radius: 0px;\n"
                                        "             padding: 6px;\n"
                                        "             height : 14px;\n"
                                        "             border-style: outset;\n"
                                        "             font : 14px;}\n")
        self.btn_teach_off.setStyleSheet("QPushButton {text-align : center;\n"
                                         "             background-color : rgb(216,216,216);\n"
                                         "             font: bold;\n"
                                         "             border-color: gray;\n"
                                         "             border-width: 2px;\n"
                                         "             border-radius: 0px;\n"
                                         "             padding: 6px;\n"
                                         "             height : 14px;\n"
                                         "             border-style: outset;\n"
                                         "             font : 14px;}\n")
        self.btn_enable_on.setStyleSheet("QPushButton {text-align : center;\n"
                                         "             background-color : rgb(216,216,216);\n"
                                         "             font: bold;\n"
                                         "             border-color: gray;\n"
                                         "             border-width: 2px;\n"
                                         "             border-radius: 15px;\n"
                                         "             padding: 6px;\n"
                                         "             height : 14px;\n"
                                         "             border-style: outset;\n"
                                         "             font : 14px;}\n")
        self.thread_receive = threading.Thread(target=self.receive_data)  # 接收拖动示教数据线程
        self.thread_receive.start()

    def btn_teach_off_click(self):
        self.btn_enable_on.setEnabled(True)
        self.btn_enable_off.setEnabled(True)
        self.btn_teach_on.setEnabled(True)  # 与拖动示教开关相反
        self.btn_teach_off.setEnabled(False)
        self.btn_teach_on.setStyleSheet("QPushButton {text-align : center;\n"
                                        "             background-color : rgb(216，216，216);\n"
                                        "             font: bold;\n"
                                        "             border-color: gray;\n"
                                        "             border-width: 2px;\n"
                                        "             border-radius: 0px;\n"
                                        "             padding: 6px;\n"
                                        "             height : 14px;\n"
                                        "             border-style: outset;\n"
                                        "             font : 14px;}\n")
        self.btn_teach_off.setStyleSheet("QPushButton {text-align : center;\n"
                                         "             background-color : red;\n"
                                         "             font: bold;\n"
                                         "             border-color: gray;\n"
                                         "             border-width: 2px;\n"
                                         "             border-radius: 0px;\n"
                                         "             padding: 6px;\n"
                                         "             height : 14px;\n"
                                         "             border-style: outset;\n"
                                         "             font : 14px;}\n")
        self.stop_thread(self.thread_receive)  # 关闭线程

    def receive_data(self):
        try:
            while True:
                time.sleep(0.1)
                nn = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
                data_count = data_ser.inWaiting()
                if data_count:
                    data = str(binascii.b2a_hex(data_ser.read(data_count)))[2:-1]
                    nn[0] = int(data[10] + data[11], 16)  # 输入16进制的数并转换成10进制
                    nn[1] = int(data[12] + data[13], 16)  # 输入16进制的数并转换成10进制
                    nn[2] = int(data[14] + data[15], 16)  # 输入16进制的数并转换成10进制
                    nn[3] = int(data[16] + data[17], 16)  # 输入16进制的数并转换成10进制
                    nn[4] = int(data[18] + data[19], 16)  # 输入16进制的数并转换成10进制
                    if 0 <= nn[0] <= 240 and 24 <= nn[1] <= 216 and 16 <= nn[2] <= 240 and 10 <= nn[3] <= 240:
                        # 添加数据
                        item1 = QStandardItem(str(nn[0]))
                        item2 = QStandardItem(str(nn[1]))
                        item3 = QStandardItem(str(nn[2]))
                        item4 = QStandardItem(str(nn[3]))
                        item5 = QStandardItem(self.lineEdit_speed.text())
                        item6 = QStandardItem('0')
                        self.label_j1.setText(str(nn[0]))
                        self.label_j2.setText(str(nn[1]))
                        self.label_j3.setText(str(nn[2]))
                        self.label_j4.setText(str(nn[3]))
                        if 50 < nn[4] <= 250:
                            item7 = QStandardItem('0')
                        elif 0 <= nn[4] <= 50:
                            item7 = QStandardItem('1')
                        self.model.appendRow([item1, item2, item3, item4, item5, item6, item7])
                data_ser.flushInput()
        except Exception as e:
            print("数据接收线程：",e)

    # endregion
    # region 使能按钮
    def btn_enable_on_click(self):
        self.btn_ini(True)
        self.btn_ini_1(True)  # 添加程序后将所有程序相关操作按钮打开
        self.btn_teach_on.setStyleSheet("QPushButton {text-align : center;\n"
                                        "             background-color : rgb(216，216，216);\n"
                                        "             font: bold;\n"
                                        "             border-color: gray;\n"
                                        "             border-width: 2px;\n"
                                        "             border-radius: 0px;\n"
                                        "             padding: 6px;\n"
                                        "             height : 14px;\n"
                                        "             border-style: outset;\n"
                                        "             font : 14px;}\n")
        self.btn_teach_on.setEnabled(False)  # 使能后不能运行拖动示教
        self.btn_teach_off.setEnabled(False)
        # self.btn_open_file.setEnabled(True)  # 打开使能后仅能加载程序和添加程序
        # self.btn_renew.setEnabled(True)
        # self.btn_add.setEnabled(True)
        robot_control.bus_servo_niuju_on(0xfe)
        degree = []
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

    def btn_enable_off_click(self):
        self.btn_ini(False)  # 使能关闭，所有的先关操作不使能
        self.btn_ini_1(False)
        self.btn_teach_on.setEnabled(True)
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
        self.btn_teach_on.setStyleSheet("QPushButton {text-align : center;\n"
                                        "             background-color : rgb(216，216，216);\n"
                                        "             font: bold;\n"
                                        "             border-color: gray;\n"
                                        "             border-width: 2px;\n"
                                        "             border-radius: 0px;\n"
                                        "             padding: 6px;\n"
                                        "             height : 14px;\n"
                                        "             border-style: outset;\n"
                                        "             font : 14px;}\n")
        robot_control.bus_servo_niuju_off(0xfe)

    # endregion
    # region 复位按钮点击事件
    def btn_reduce_click(self):
        self.btn_ini(False)
        self.btn_ini_1(False)
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
        self.btn_teach_on.setStyleSheet("QPushButton {text-align : center;\n"
                                        "             background-color : rgb(216，216，216);\n"
                                        "             font: bold;\n"
                                        "             border-color: gray;\n"
                                        "             border-width: 2px;\n"
                                        "             border-radius: 0px;\n"
                                        "             padding: 6px;\n"
                                        "             height : 14px;\n"
                                        "             border-style: outset;\n"
                                        "             font : 14px;}\n")
        self.btn_teach_off.setStyleSheet("QPushButton {text-align : center;\n"
                                         "             background-color : rgb(216，216，216);\n"
                                         "             font: bold;\n"
                                         "             border-color: gray;\n"
                                         "             border-width: 2px;\n"
                                         "             border-radius: 0px;\n"
                                         "             padding: 6px;\n"
                                         "             height : 14px;\n"
                                         "             border-style: outset;\n"
                                         "             font : 14px;}\n")

    # endregion
    # region 运行按钮点击事件
    def btn_run_click(self):
        robot_control.bus_servo_niuju_on(0xfe)  # 使能打开
        self.btn_teach_on.setEnabled(False)
        self.btn_teach_off.setEnabled(False)
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
                                          "             background-color : rgb(216，216，216);\n"
                                          "             font: bold;\n"
                                          "             border-color: gray;\n"
                                          "             border-width: 2px;\n"
                                          "             border-radius: 15px;\n"
                                          "             padding: 6px;\n"
                                          "             height : 14px;\n"
                                          "             border-style: outset;\n"
                                          "             font : 14px;}\n")
        self.btn_teach_on.setStyleSheet("QPushButton {text-align : center;\n"
                                        "             background-color : rgb(216，216，216);\n"
                                        "             font: bold;\n"
                                        "             border-color: gray;\n"
                                        "             border-width: 2px;\n"
                                        "             border-radius: 15px;\n"
                                        "             padding: 6px;\n"
                                        "             height : 14px;\n"
                                        "             border-style: outset;\n"
                                        "             font : 14px;}\n")
        self.btn_ini_2(False)  # 程序运行过程中其他按钮不使能，除了停止外
        self.btn_ini(False)  # 控制部分不使能
        try:
            rowCount = self.model.rowCount()
            colCount = self.model.columnCount()
            global item
            test = []
            for i in range(0, rowCount):
                # self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
                # self.tableView.setStyleSheet("selection-background-color:rgb(0,150,200)")
                # self.tableView.selectRow(i)
                for j in range(0, colCount):
                    test.append(self.model.index(i, j).data())
                item.append(test)
                test = []  # 清除速度，不累加
        except Exception as e:
            print(e)

    def send_robot_data(self):
        try:
            while True:
                time.sleep(0.1)
                value = self.lineEdit_recur.text()
                if value == "":
                    value = '1'
                for t in range(0, int(value)):
                    global item
                    for i in range(0, len(item)):
                        # 判断表格数据是否是数值类型，防止发送数据线程报错
                        if self.is_number(item[i][0]) == True and self.is_number(item[i][1]) == True and self.is_number(
                                item[i][2]) == True and self.is_number(item[i][3]) == True and self.is_number(
                                item[i][4]) == True and self.is_number(item[i][5]) == True and self.is_number(
                                item[i][6]) == True:
                            if isRunStop:
                                if int(item[i][6]) == 0:
                                    clip_value = 100  # 夹爪关
                                else:
                                    clip_value = 0  # 夹爪开
                                if int(item[i][5]) >= 500:
                                    time.sleep(int(item[i][5]) / 1000)
                                else:
                                    time.sleep(0.5)
                                if 0<=int(item[i][0])<=240 and 24<=int(item[i][1])<=216 and 16<=int(item[i][2])<=240 and 10<=int(item[i][3])<=240:
                                    robot_control.bus_servo_all(int(item[i][0]), int(item[i][1]), int(item[i][2]),
                                                                int(item[i][3]),
                                                                clip_value, int(item[i][4]))
                                    self.label_j1.setText(item[i][0])
                                    self.label_j2.setText(item[i][1])
                                    self.label_j3.setText(item[i][2])
                                    self.label_j4.setText(item[i][3])
                                    self.lineEdit_recur.setText(str(int(value) - t))#程序执行次数递减
                item = []
        except Exception as e:
            print("数据发送线程：",e)

    def btn_stop_click(self):

        global isRunStop
        if isRunStop == True:
            isRunStop = False
            self.btn_stop.setText("开始")
            self.btn_run.setEnabled(False)
        else:
            isRunStop = True
            self.btn_stop.setText("停止")
            self.btn_ini_2(True)
            self.btn_ini(True)
        print(isRunStop)

    # endregion
    # region 单步运行按钮事件
    def btn_step_click(self):
        try:
            index = self.tableView.currentIndex()  # 取得当前选中行的index
            row = index.row()  # 当前行
            colCount = self.model.columnCount()  # 所有列
            test = []
            for i in range(0, colCount):
                test.append(self.model.index(row, i).data())
            # 判断单元格是否是数值类型切是否在角度范围内
            if self.is_number(test[0]) == True and self.is_number(test[1]) == True and self.is_number(
                test[2]) == True and self.is_number(test[3]) == True and self.is_number(
                test[4]) == True and self.is_number(test[5]) == True and self.is_number(test[6]) == True:
                if int(test[6]) == 0:
                    clip_value = 100  # 夹爪关
                else:
                    clip_value = 0  # 夹爪开
                if int(test[5]) >= 500:
                    time.sleep(int(test[5]) / 1000)
                else:
                    time.sleep(0.5)
                if 0 <= int(test[0]) <= 240 and 24 <= int(test[1]) <= 216 and 16 <= int(test[2]) <= 240 and 10 <= int(test[3]) <= 240:
                    robot_control.bus_servo_all(int(test[0]), int(test[1]), int(test[2]), int(test[3]), clip_value,
                                                int(test[4]))
                    self.label_j1.setText(test[0])
                    self.label_j2.setText(test[1])
                    self.label_j3.setText(test[2])
                    self.label_j4.setText(test[3])
                    test = []
        except Exception as e:
            print(e)

    # endregion
    # region 更新按钮事件
    def btn_renew_click(self):
        index = self.tableView.currentIndex()  # 取得当前选中行的index
        if index != None:
            self.model.setItem(index.row(), 0, QStandardItem(self.label_j1.text()))
            self.model.setItem(index.row(), 1, QStandardItem(self.label_j2.text()))
            self.model.setItem(index.row(), 2, QStandardItem(self.label_j3.text()))
            self.model.setItem(index.row(), 3, QStandardItem(self.label_j4.text()))
            self.model.setItem(index.row(), 4, QStandardItem(self.lineEdit_speed.text()))

    # endregion
    # region 归零按钮事件
    def btn_zero_click(self):
        wait_point = [38, 45, 182, 219, 0, 1000]
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
        self.btn_teach_on.setEnabled(True)
        # self.btn_enable_on.setStyleSheet("QPushButton {text-align : center;\n"
        #                                  "             background-color : rgb(216，216，216);\n"
        #                                  "             font: bold;\n"
        #                                  "             border-color: gray;\n"
        #                                  "             border-width: 2px;\n"
        #                                  "             border-radius: 15px;\n"
        #                                  "             padding: 6px;\n"
        #                                  "             height : 14px;\n"
        #                                  "             border-style: outset;\n"
        #                                  "             font : 14px;}\n")
        # self.btn_enable_off.setStyleSheet("QPushButton {text-align : center;\n"
        #                                   "             background-color : red;\n"
        #                                   "             font: bold;\n"
        #                                   "             border-color: gray;\n"
        #                                   "             border-width: 2px;\n"
        #                                   "             border-radius: 15px;\n"
        #                                   "             padding: 6px;\n"
        #                                   "             height : 14px;\n"
        #                                   "             border-style: outset;\n"
        #                                   "             font : 14px;}\n")

    # endregion
    # region 单元格相关操作
    def tableView_init(self):
        # self.tableView.setAlternatingRowColors(True)
        # 4行3列
        self.model = QStandardItemModel(0, 0)
        # 设置表头
        self.model.setHorizontalHeaderLabels(
            ['关节1(0-240°)', '关节2(24-216°)', '关节3(16-240°)', '关节4(10-240°)', '速度(ms/deg)', '延迟(ms)', '夹爪(开/关)'])
        # 列宽自适应充满表格
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 所有列自动拉伸，充满界面
        # self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)  # 设置只能单个
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)  # 设置只能选中整行
        # 关联QTableView控件和Model
        self.tableView.setModel(self.model)

        layout = QVBoxLayout()
        layout.addWidget(self.tableView)
        self.setLayout(layout)
    # 下移行
    def btn_move_down_click(self):
        index = self.tableView.currentIndex()  # 取得当前选中行的index
        row = index.row()
        if row < self.model.rowCount() - 1:
            self.model.insertRow(row + 2)
            for i in range(self.model.columnCount()):
                self.model.setItem(row + 2, i, self.model.takeItem(row, i))
            self.model.removeRow(row)

    # 上移行
    def btn_move_up_click(self):
        index = self.tableView.currentIndex()  # 取得当前选中行的index
        row = index.row()
        if row > 0:
            self.model.insertRow(row - 1)
            for i in range(self.model.columnCount()):
                self.model.setItem(row - 1, i, self.model.takeItem(row + 1, i))
            self.model.removeRow(row + 1)

    # 添加行
    def btn_add_click(self):
        # 添加数据
        item1 = QStandardItem(self.label_j1.text())
        item2 = QStandardItem(self.label_j2.text())
        item3 = QStandardItem(self.label_j3.text())
        item4 = QStandardItem(self.label_j4.text())
        item5 = QStandardItem(self.lineEdit_speed.text())
        item6 = QStandardItem('0')
        item7 = QStandardItem('1')
        self.model.appendRow([item1, item2, item3, item4, item5, item6, item7])
    #插入行
    def btn_insert_click(self):
        # 插入数据
        item1 = QStandardItem(self.label_j1.text())
        item2 = QStandardItem(self.label_j2.text())
        item3 = QStandardItem(self.label_j3.text())
        item4 = QStandardItem(self.label_j4.text())
        item5 = QStandardItem(self.lineEdit_speed.text())
        item6 = QStandardItem('0')
        item7 = QStandardItem('1')
        index = self.tableView.currentIndex()  # 取得当前选中行的index
        row = index.row()
        self.model.insertRow(row + 1, [item1, item2, item3, item4, item5, item6, item7])  # 当前行插入数据
    # 删除行
    def btn_del_click(self):
        index = self.tableView.currentIndex()  # 取得当前选中行的index
        self.model.removeRow(index.row())  # 通过index的row()操作得到行数进行删除

    # 清除所有行
    def btn_clear_click(self):
        # 会全部清空，包括那个标准表头
        self.model.clear()
        # 设置表头
        self.model.setHorizontalHeaderLabels(
            ['关节1(0-240°)', '关节2(24-216°)', '关节3(16-240°)', '关节4(10-240°)', '速度(ms/deg)', '延迟(ms)', '夹爪(开/关)'])

    # 复制
    def btn_copy_click(self):
        text = self.selected_tb_text()  # 获取当前表格选中的数据
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            # pyperclip.copy(text) # 复制数据到粘贴板

    # 粘贴
    def btn_stick_click(self):
        self.paste_tb_text()

    # 复制单元格文本
    def paste_tb_text(self):
        try:
            indexes = self.tableView.selectedIndexes()  # 获取表格对象中被选中的数据索引列表
            for index in indexes:
                index = index
                break
            r, c = index.row(), index.column()
            text = QApplication.clipboard().text()
            ls = text.split('\n')
            ls1 = []
            for row in ls:
                ls1.append(row.split('\t'))
            model = self.tableView.model()
            rows = len(ls)
            columns = len(ls1[0])
            for row in range(rows):
                for column in range(columns):
                    item = QStandardItem()
                    item.setText((str(ls1[row][column])))
                    model.setItem(row + r, column + c, item)
        except Exception as e:
            print(e)
            return

    # 选择单元格文本
    def selected_tb_text(self):
        try:
            indexes = self.tableView.selectedIndexes()  # 获取表格对象中被选中的数据索引列表
            indexes_dict = {}
            for index in indexes:  # 遍历每个单元格
                row, column = index.row(), index.column()  # 获取单元格的行号，列号
                if row in indexes_dict.keys():
                    indexes_dict[row].append(column)
                else:
                    indexes_dict[row] = [column]

            # 将数据表数据用制表符(\t)和换行符(\n)连接，使其可以复制到excel文件中
            text = ''
            for row, columns in indexes_dict.items():
                row_data = ''
                for column in columns:
                    data = self.tableView.model().item(row, column).text()
                    if row_data:
                        row_data = row_data + '\t' + data
                    else:
                        row_data = data

                if text:
                    text = text + '\n' + row_data
                else:
                    text = row_data
            return text
        except BaseException as e:
            print(e)
            return ''

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
    # region程序保存
    def btn_save_file_click(self):
        try:
            rowCount = self.model.rowCount()
            colCount = self.model.columnCount()
            test = []
            # 创建一个txt文件，文件名为first file,并向文件写入msg
            now_time = time.strftime('%Y-%m-%d-%H-%M-%S-%M', time.localtime(time.time()))  # 获取系统时间
            program_name = self.lineEdit_file_name.text()
            if program_name == "":  # 判断程序文件名是否为空，如果为空就以当前时间保存为文件名
                program_name = now_time
            file = open('ProgramFile/program_' + str(program_name) + '.txt', 'w').close()  # 清空程序文件
            for i in range(0, rowCount):  # 一行一行写入txt,方便txt读取
                for j in range(0, colCount):
                    test.append(self.model.index(i, j).data())
                with open('ProgramFile/program_' + str(program_name) + '.txt', "a", encoding='utf-8') as f:  # 追加写入
                    f.write(str(test))
                    f.write('\n')
                test = []  # 清除数据，不累加
        except Exception as e:
            print(e)

    # endregion
    # region 打开程序
    def btn_open_file_click(self):
        try:
            root = tkinter.Tk()
            root.withdraw()
            filename = filedialog.askopenfilename(initialdir = 'ProgramFile')
            list = []
            with open(filename, 'r') as f:
                self.btn_clear_click()  # 清除所有行，再写入
                my_data = f.readlines()  # txt中所有字符串读入my_data，得到的是一个list
                for line in my_data:  # 将文本字符串转成数组字符串
                    line = line.strip()  # 移除字符串头尾
                    line = line.strip("[]")  # 移除字符串头尾[]
                    line_data = line.split(',')  # 按照逗号分隔
                    line = line.strip()  # 移除字符串头尾引号
                    list.append(line_data)  # 添加到数组
                all_list = []  # 字符串数组转为整型后所有行的数组
                single_list = []  # 保存每一行转换的数组
                for i in range(0, len(list)):  # 将数组字符串转数组整型，eval去掉引号并转为整型：‘1’→1
                    for j in range(0, len(list[i])):
                        value = int(eval(list[i][j]))
                        single_list.append(value)
                    all_list.append(single_list)
                    single_list = []
                for i in range(0, len(all_list)):
                    for j in range(0, len(all_list[i])):
                        self.model.setItem(i, j, QStandardItem(str(all_list[i][j])))  # 将数据填充到每一个单元格
        except Exception as e:
            print(e)

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
    # region退出程序，关闭线程
    def closeEvent(self, event):
        if self.thread_run_stop.is_alive():
            self.stop_thread(self.thread_run_stop)  # 关闭线程
        if self.thread_receive.is_alive():
            self.stop_thread(self.thread_receive)  # 关闭线程
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