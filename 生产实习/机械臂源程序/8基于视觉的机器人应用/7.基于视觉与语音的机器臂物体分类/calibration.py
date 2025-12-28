import cv2
import numpy as np
#region 相机与世界坐标系标定
class Cam_Calibration():
    def calibration(self,x, y):#填写中心点的像素值和世界坐标得到转换关系
        # 相机坐标
        pixel1_x = 161
        pixel1_y = 36

        pixel2_x = 467
        pixel2_y = 35

        pixel3_x = 317
        pixel3_y = 346

        # 世界坐标（机械臂坐标）
        point1_X = 2.5
        point1_Y = 2.5
        point2_X = -2.5
        point2_Y = 2.5
        point3_X = 0
        point3_Y = 7.5
        #坐标转为数组
        pts1 = np.float32([[pixel1_x, pixel1_y], [pixel2_x, pixel2_y], [pixel3_x, pixel3_y]])
        pts2 = np.float32([[point1_X, point1_Y], [point2_X, point2_Y], [point3_X, point3_Y]])
        M = cv2.getAffineTransform(pts1, pts2)  # 仿射变化，仿射矩阵为2*3
        print(M)

        zuobiao = np.dot(M, [x, y, 1])  # 仿射逆变换，得到坐标（x,y)
        ka = int(zuobiao[0])
        kb = int(zuobiao[1])
        return ka, kb
#endregion