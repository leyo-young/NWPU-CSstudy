import time
from Five_Robot_Control import *

robot_control = Five_Robot_Control()
if __name__ == "__main__":
    robot_control.bus_servo_niuju_on(0xfe)#先使能
    time.sleep(2)
    robot_control.bus_servo_all(38, 45, 182, 219, 100, 1000)
    time.sleep(2)
    robot_control.bus_servo_all(38, 90, 182, 219, 0, 1000)
    time.sleep(2)
    robot_control.bus_servo_all(38, 45, 182, 219, 100, 1000)
    time.sleep(2)
    robot_control.bus_servo_all(113, 75, 182, 219, 0, 1000)
    time.sleep(2)
    robot_control.bus_servo_all(200, 75, 182, 219, 100, 1000)
    time.sleep(2)
    robot_control.bus_servo_all(113, 120, 167, 200, 0, 1000)
    time.sleep(2)
    robot_control.bus_servo_all(38, 45, 182, 219, 100, 1000)
