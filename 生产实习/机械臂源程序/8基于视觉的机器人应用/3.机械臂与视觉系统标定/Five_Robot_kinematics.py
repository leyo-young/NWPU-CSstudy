import math
import time
#region机械臂参数
#机械臂4连杆长度定义，单位厘米
P = 4.3
A1 = 2.6
A2 = 6.3
A3 = 6.3
A4 = 15
MAX_LEN = A2+A3+A4
MAX_HIGH = A1+A2+A3+A4
#endregion
#region 机械臂正逆解
class Five_Robot_kinematics():
    def cos(self,degree):
        return math.cos(math.radians(degree))
    def sin(self,degree):
        return math.sin(math.radians(degree))
    def atan2(self,v1,v2):
        rad=math.atan2(v1,v2)
        return math.degrees(rad)
    def _j_degree_convert(self,joint,j_or_deg):#对公式的角度进行转换补偿
        # 将j1-j4和机械臂的角度表达互换
        if joint == 1:
            res = j_or_deg - 60
        elif joint == 2:
            res = j_or_deg + 30
        elif joint == 3:
            res = j_or_deg + 126
        elif joint == 4:
            res = j_or_deg + 98
        else:
            # 只适用于1-4关节
            raise ValueError
        return res
    def _valid_degree(self,joint,degree):
        if 40 <= degree <= 120:
            return True

        else:
            print('joint {} is invalid degree {}'.format(joint,degree))
            return False
    def _valid_j(self,joint,j):
        if j is None:
            return False
        degree = self._j_degree_convert(joint,j)
        if 0 <= degree <= 240:
            return True
        else:
            print('joint {} is invalid j:{} degree {}'.format(joint,j,degree))
            return False
    def _out_of_range(self,lengh,height):
        if height>MAX_HIGH:
            print('高度 {} 超过界限 {}'.format(height,MAX_HIGH))
            return True
        if lengh > MAX_LEN:
            print('投影长度 {} 超过界限 {}'.format(lengh,MAX_LEN))
            return True
        return False
    def _calculate_j1(self,x,y,z):
        length=round(math.sqrt(pow((y+P),2)+pow(x,2)),2)

        if length ==0:
            j1=0 #可以是任意数
        else:
            j1=self.atan2((y+P),x)
        hight = z
        return j1,length,hight
    def _calculate_j4(self,L, H):
        cos4 = (L**2 + H**2 - A3**2 - A4**2)/(2*A3*A4)
        sin4 = math.sqrt(1 - cos4 ** 2)
        j4 = self.atan2(sin4, cos4)
        return j4
    def _calculate_j3(self,L, H,j4):
        K1 = A3 + A4*self.cos(j4)
        K2 = A4*self.sin(j4)
        w = self.atan2(K2,K1)
        j3 =self.atan2(L,H) -w+30
        return j3
    def _xyz_alpha_to_j123(self,x,y,z):#固定角2，得到角3和角4的关系并进行转换
        valid = False
        j1, j2, j3, j4 = None, 30, None, None
        j1, length, height = self._calculate_j1(x,y,z)
        if self._valid_j(1,j1) and not self._out_of_range(length,height):
            H = height - A2 * self.cos(j2) - A1
            L = length + A2 * self.sin(j2)
            j4 = self._calculate_j4(L, H)
            if self._valid_j(4,j4):
                j3 = self._calculate_j3(L, H, j4)
                if self._valid_j(2,j2):
                    j2 = 90-j2
                    valid = True
        return valid, j1, j2, j3, j4
    def _xyz_to_j123(self,x,y,z):
        #MIN_ALPHA = 90 # j2+j3+j4 min value, 最后一个joint不向后仰
        valid = False
        j1, j2, j3, j4 = None, None, None, None
        while not valid:
            valid, j1, j2, j3, j4 = self._xyz_alpha_to_j123(x,y,z)
        return valid, j1, j2, j3, j4
    def backward_kinematics(self,x, y, z):#由坐标推出角度
        x=float(x)
        y=float(y)
        z=float(z)
        #print('x:{} y:{} z:{} '.format(x,y,z))

        if y<0:
            print('y 不能小于0')
            raise ValueError
        valid, j1, j2, j3, j4 = self._xyz_to_j123(x,y,z)
        deg1, deg2, deg3, deg4 = None, None, None, None
        if valid:
            deg1 = round(self._j_degree_convert(1,j1),0)
            deg2 = round(self._j_degree_convert(2,j2),0)
            deg3 = round(self._j_degree_convert(3,j3),0)
            deg4 = round(self._j_degree_convert(4,j4),0)
        #print('valid:{},deg1:{},deg2:{},deg3:{},deg4:{}'.format(valid,deg1,deg2,deg3,deg4))
        #print('{},{},{},{}'.format(deg1,deg2,deg3,deg4))
        return valid, deg1, deg2, deg3, deg4
    def forward_kinematics(self,deg1,deg3,deg4):#验证
        valid = False
        if not self._valid_degree(1,deg1) or not self._valid_degree(3,deg3) or not self._valid_degree(4,deg4):
            return valid,None,None,None
        j1=self._j_degree_convert(1,deg1) +60
        j3=self._j_degree_convert(3,deg3) - 126
        j4=self._j_degree_convert(4,deg4) - 98
        height = A1 + A2*self.cos(30) + A3*self.cos(j3-30) + A4*self.cos(j4+j3-30)
        length = - A2*self.sin(30) + A3*self.sin(j3-30) + A4*self.sin(j4+j3-30)

        z = round(height,2)
        x = round(length*self.cos(j1))
        y = round(length*self.sin(j1)-P)

        # 世界坐标的边界
        if 0<=y and z>=0:
            valid = True
        print('valid:{},x:{},y:{},z:{},lenghth:{},height:{},alpha:{}'.format(valid,x,y,z,round(length,2),round(height,2)))
        return valid,x,y,z
    def arr(self,x,y,z):
        arr = self.backward_kinematics(x,y,z)
        arr1 = int(arr[1])
        arr2 = int(arr[2])
        arr3 = int(arr[3])
        arr4 = int(arr[4])
        #print(int(arr[1]),int(arr[2]),int(arr[3]),int(arr[4]))
        #print('done')
        return arr1,arr2,arr3,arr4
#endregion