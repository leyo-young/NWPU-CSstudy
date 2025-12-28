import _thread  # 导入线程包
import serial
import time
from Five_Robot_Control import *

robot_control = Five_Robot_Control()
data_ser = serial.Serial("/dev/user_voice", 115200, timeout=5)  # 语音板串口
data_ser.flushInput()
robot_control.bus_servo_niuju_on(0xfe)


while True:
    try:
        data_count = data_ser.inWaiting()
        if data_count != 0:
            recv = data_ser.read(data_ser.in_waiting).decode("gbk")
            result = recv.split()
            print(result[0])
            if (result[0] == "AA_xiang-qian_BB"):
                robot_control.bus_servo(1, 30, 100)
                print("机械臂向前")

            elif (result[0] == "AA_xiang-hou_BB"):
                robot_control.bus_servo(1, 200, 100)
                print("机械臂向后")

            elif (result[0] == "AA_xiang-zuo_BB"):
                robot_control.bus_servo(1, 240, 100)
                print("机械臂向左")
            elif (result[0] == "AA_xiang-you_BB"):
                robot_control.bus_servo(1, 120, 100)
                print("机械臂向右")
    except:
        print("error")
