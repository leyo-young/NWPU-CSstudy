from recognition import recognition
from training import training
from datasets import datasets
from delFile import del_file
import serial
import time
data_ser = serial.Serial("/dev/user_robot", 115200, timeout=5)  # 插入传感器自动识别设备，并设置波特率
def main():
    bus_bjdj(0x5A)
    facedict = {}
    cur_path = r'./dataset/'
    while True:
        print('*' * 31)
        print('''
            人脸录入与识别
            --------------
            输入1,人脸采集
            输入2,人脸训练
            输入3,人脸识别
            输入d,删除数据
            输入q,退出程序      
        ''')
        print('*' * 31)
        num = input("请输入您的操作选择: ")
        if num == '1':
            mydict = datasets()
            facedict.update(mydict)
            print(facedict)
        elif num == '2':
            training()
        elif num == '3':
            recognition(facedict)
        elif num == 'd':
            del_file(cur_path)
        elif num == 'q':
           print("退出程序成功!")
           break
        else:
            print("您输入有误,请重新输入!")

def bus_bjdj(value):  # 步进电机位置控制（id，位置）0-315mm
    ddata = [0xFF,0xFE,0x02,0x01,0x00,0x01,0x46,0x00,0x0D,0x0A]
    ddata[5] = value
    data_ser.write(ddata)
    time.sleep(0.1)
if __name__ == '__main__':
    main()