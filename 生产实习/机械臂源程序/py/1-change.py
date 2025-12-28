import time
import threading
from Five_Robot_Control import *
from calibration import *
from Five_Robot_kinematics import *
import queue

# 初始化对象
robot_control = Five_Robot_Control()
calibration = Cam_Calibration()
five_robot_kinematics = Five_Robot_kinematics()

# 共享队列
shared_queue = None

def robot_pick(pixel_x, pixel_y):
    point_x, point_y = calibration.calibration(pixel_x, pixel_y)  # 像素坐标得到世界坐标
    arr1, arr2, arr3, arr4 = five_robot_kinematics.arr(point_x, point_y, 0)  # 最后一个为Z轴，输出四个角度
    robot_control.bus_servo_niuju_on(0xfe)
    time.sleep(0.5)
    robot_control.bus_servo_all(30, 58, 170, 217, 0, 1000)
    time.sleep(2)
    robot_control.bus_servo_all(arr1, arr2, arr3, arr4, 0, 1000)
    time.sleep(2)

def robot_control_loop():
    while True:
        if not shared_queue.empty():
            cx, cy = shared_queue.get()
            print(f"Received: cx={cx}, cy={cy}")
            robot_pick(cx, cy)
        time.sleep(0.1)  # 控制循环间隔

if __name__ == "__main__":
    # 获取共享队列
    from detectp2 import shared_queue

    # 启动机器人控制线程
    robot_control_thread = threading.Thread(target=robot_control_loop)
    robot_control_thread.start()