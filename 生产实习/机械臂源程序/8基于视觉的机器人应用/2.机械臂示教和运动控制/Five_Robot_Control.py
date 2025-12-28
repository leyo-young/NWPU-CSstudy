import _thread  # 导入线程包
import serial
import time
import binascii
# Arduino接收的串口
data_ser = serial.Serial("/dev/user_robot", 115200, timeout=5)
class Five_Robot_Control():
    # 舵机控制（id，角度，时间）
    def bus_servo(self,idd, jioa, tim):
            ddata = [0xFF, 0xFE, 0x01, 0x01, 0x00, 0x01, 0xff, 0x03, 0xE8, 0x0D, 0x0A]
            ddata[5] = idd
            ddata[6] = jioa
            ddata[7] = int(tim / 256)
            ddata[8] = tim % 256
            data_ser.write(ddata)
            time.sleep(0.1)
    # 舵机读取
    def bus_servo_get(self,idd):
        data_ser.flushInput()
        ddata = [0xFF, 0xFE, 0x01, 0x02, 0xFF, 0x01, 0x0D, 0x0A]
        ddata[5] = idd
        data_ser.write(ddata)
        time.sleep(0.3)
        data_count = data_ser.inWaiting()
        if data_count:
            data = str(binascii.b2a_hex(data_ser.read(data_count)))[2:-1]
            nn = int(data[10] + data[11], 16)  # 输入16进制的数并转换成10进制
            print(nn)
            print("data_ok")
        else:
            nn = 0xFF
            print("data_error")
        data_ser.flushInput()
        time.sleep(0.1)
        return nn;

    # 舵机同时控制（1，2，3，4，5，时间）
    def bus_servo_all(self,a, b, c, d, e, tim):
        ddata = [0xFF, 0xFE, 0x01, 0x01, 0x00, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0xE8, 0x0D, 0x0A]
        ddata[6] = a
        ddata[7] = b
        ddata[8] = c
        ddata[9] = d
        ddata[10] = e
        ddata[11] = int(tim / 256)
        ddata[12] = tim % 256
        data_ser.write(ddata)
        time.sleep(0.1)

    # 舵机同时读取
    def bus_servo_get_all(self):
        data_ser.flushInput()
        ddata = [0xFF, 0xFE, 0x01, 0x02, 0xFF, 0xFF, 0x0D, 0x0A]
        nn = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        data_ser.write(ddata)
        time.sleep(0.4)
        data_count = data_ser.inWaiting()
        if data_count:
            data = str(binascii.b2a_hex(data_ser.read(data_count)))[2:-1]
            nn[0] = int(data[10] + data[11], 16)  # 输入16进制的数并转换成10进制
            nn[1] = int(data[12] + data[13], 16)  # 输入16进制的数并转换成10进制
            nn[2] = int(data[14] + data[15], 16)  # 输入16进制的数并转换成10进制
            nn[3] = int(data[16] + data[17], 16)  # 输入16进制的数并转换成10进制
            nn[4] = int(data[18] + data[19], 16)  # 输入16进制的数并转换成10进制
        else:
            nn[0] = 0xFF
            nn[1] = 0xFF
            nn[2] = 0xFF
            nn[3] = 0xFF
            nn[4] = 0xFF
        data_ser.flushInput()
        time.sleep(0.1)
        return nn

    # 扭矩关闭（舵机编号）0xfe为全部控制
    def bus_servo_niuju_off(self,idd):
        ddata = [0xFF, 0xFE, 0x01, 0x03, 0xFF, 0xFE, 0x00, 0x0D, 0x0A]
        ddata[5] = idd
        data_ser.write(ddata)
        time.sleep(0.1)

    # 扭矩开启（舵机编号）0xfe为全部控制
    def bus_servo_niuju_on(self,idd):
        ddata = [0xFF, 0xFE, 0x01, 0x03, 0xFF, 0xFE, 0x01, 0x0D, 0x0A]
        ddata[5] = idd
        data_ser.write(ddata)
        time.sleep(0.1)

    # 云台控制（角度，角度）
    def bus_yuntai(self,a, b):
        ddata = [0xFF, 0xFE, 0x02, 0x01, 0xff, 0x00, 0x00, 0x0D, 0x0A]
        ddata[5] = a
        ddata[6] = b
        data_ser.write(ddata)
        time.sleep(0.1)

    # 机械臂开启
    def bus_servo_pwr_on(self):
        ddata = [0xFF, 0xFE, 0x01, 0xFF, 0x0D, 0x0A]
        data_ser.write(ddata)
        time.sleep(0.1)

    # 云台开启
    def bus_yuntai_pwr_on(self):
        ddata = [0xFF, 0xFE, 0x02, 0xFF, 0x0D, 0x0A]
        data_ser.write(ddata)
        time.sleep(0.1)

    # 复位
    def bus_pwr_off(self):
        ddata = [0xFF, 0xFE, 0xFF, 0xFF, 0x0D, 0x0A]
        data_ser.write(ddata)
        time.sleep(0.1)
    # def control(self,x, y):
    #     x, y = calibration.calibration(x, y)  # 像素坐标得到世界坐标
    #     arr1, arr2, arr3, arr4 = degree_convert.arr(x, y, 0)  # 最后一个为Z轴，输出四个角度
    #     self.bus_servo_pwr_on()
    #     self.bus_servo_niuju_on(0xfe)
    #     time.sleep(2)
    #     self.bus_servo_all(30, 60, 170, 200, 0, 1000)
    #     time.sleep(2)
    #     self.bus_servo_all(arr1, arr2, arr3, arr4, 0, 1000)
    #     time.sleep(2)
    #     self.bus_servo_all(arr1, arr2, arr3, arr4, 80, 1000)
    #     time.sleep(2)
    #     self.bus_servo_all(30, 60, 170, 200, 80, 1000)
