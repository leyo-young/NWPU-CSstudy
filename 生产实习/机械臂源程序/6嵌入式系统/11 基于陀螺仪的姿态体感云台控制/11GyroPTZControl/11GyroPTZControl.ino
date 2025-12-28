#include <Arduino.h>
#include <U8g2lib.h>

#ifdef U8X8_HAVE_HW_SPI
#include <SPI.h>
#endif
#ifdef U8X8_HAVE_HW_I2C
#include <Wire.h>
#endif
//选择屏幕型号1.3寸SH1106 OLED屏幕
U8G2_SH1106_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, /* reset=*/ U8X8_PIN_NONE);
#include <Servo.h>

// 创建两个舵机对象
Servo myservo1, myservo2; 
int pos = 0;    // 角度存储变量
int DJ_X = 8, DJ_Y = 9;//定义两个舵机控制引脚为CPU 8号和9号引脚

#include "I2Cdev.h"
#include "MPU6050_6Axis_MotionApps20.h"

#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE  
#include "Wire.h"
#endif

//创建陀螺仪
MPU6050 mpu;
//MPU6050 mpu(0x69); // <-- use for AD0 high
#define OUTPUT_READABLE_YAWPITCHROLL

#define INTERRUPT_PIN 50  // use pin 2 on Arduino Uno & most boards

bool blinkState = false;

// MPU 控制/状态变量
bool dmpReady = false;  // 若DMP初始化成功，设置为true
uint8_t mpuIntStatus;   // MPU中断状态
uint8_t devStatus;      // 设备运行状态 (0 = success, !0 = error)
uint16_t packetSize;    // 预留DMP 数据包大小 (默认 42 字节)
uint16_t fifoCount;     // FIFO计数器
uint8_t fifoBuffer[64]; // FIFO 存储缓冲区

// orientation/motion vars
Quaternion q;           // [w, x, y, z]         四元数
VectorInt16 aa;         // [x, y, z]            加速度传感器测量值
VectorInt16 aaReal;     // [x, y, z]            无重力加速度传感器测量值
VectorInt16 aaWorld;    // [x, y, z]            通用坐标传感器测量值
VectorFloat gravity;    // [x, y, z]            重力矢量
float euler[3];         // [psi, theta, phi]    欧拉角
float ypr[3];           // [yaw, pitch, roll]   航向角/俯仰角/横滚角和重力矢量

// packet structure for InvenSense teapot demo
uint8_t teapotPacket[14] = { '$', 0x02, 0, 0, 0, 0, 0, 0, 0, 0, 0x00, 0x00, '\r', '\n' };


volatile bool mpuInterrupt = false;     // 赋MPU中断初值为false
void dmpDataReady() {
  mpuInterrupt = true;
}
///////////////////////////////////////////////////////////////////////////////////////

float cube[8][3] = {{ -15, -15, -15}, { -15, 15, -15}, {15, 15, -15}, {15, -15, -15}, { -15, -15, 15}, { -15, 15, 15}, {15, 15, 15}, {15, -15, 15}}; //立方体各点坐标
int lineid[] = {1, 2, 2, 3, 3, 4, 4, 1, 5, 6, 6, 7, 7, 8, 8, 5, 8, 4, 7, 3, 6, 2, 5, 1}; //记录点之间连接顺序
//计算立方体矩阵乘法
float* matconv(float* a, float b[3][3]) {
  float res[3];
  for (int i = 0; i < 3; i++)
    res[i] = b[i][0] * a[0] + b[i][1] * a[1] + b[i][2] * a[2];
  for (int i = 0; i < 3; i++)a[i] = res[i];
  return a;
}
//旋转立方体向量函数
void rotate(float* obj, float x, float y, float z) { 
  x /= PI; y /= PI; z /= PI;
  float rz[3][3] = {{cos(z), -sin(z), 0}, {sin(z), cos(z), 0}, {0, 0, 1}};
  float ry[3][3] = {{1, 0, 0}, {0, cos(y), -sin(y)}, {0, sin(y), cos(y)}};
  float rx[3][3] = {{cos(x), 0, sin(x)}, {0, 1, 0}, { -sin(x), 0, cos(x)}};
  matconv(matconv(matconv(obj, rz), ry), rx);
}
int KEY1 = 4;//定义按键KEY1为4号引脚
int KEY2 = 5;//定义按键KEY2为5号引脚
int KEY3 = 6;//定义按键KEY3为6号引脚
float m_x, m_y, m_z;//定义陀螺仪俯仰角、横滚角、航向角缓存变量
float am_x, am_y, am_z;//定义陀螺仪俯仰角、横滚角、航向角变量
int dj_qiy = 0;//云台启动信号，初始化为0，未启动
float dj_x, dj_y, dj_z;//定义舵机变
void setup() {
  u8g2.begin();//构造u8g2模式：初始化显示器，重置清屏，唤醒屏幕
  pinMode(KEY1, INPUT);//设置KEY1引脚为输入引脚
  pinMode(KEY2, INPUT);//设置KEY2引脚为输入引脚
  pinMode(KEY3, INPUT);//设置KEY3引脚为输入引脚
  myservo1.attach(DJ_X);  // 控制线连接数字9
  myservo2.attach(DJ_Y);  // 控制线连接数字8
  u8g2.clearBuffer();          // 清显示屏缓冲区

  u8g2.setFont(u8g2_font_6x10_mf  ); // 设置字体
  u8g2.setCursor(0, 10);
  u8g2.print("MPU6050...");//显示"MPU6050..."
  u8g2.sendBuffer();          // 发送缓冲区数据至显示器，发刷新消息
 // 连接IIC总线， (IIC设备库不会自动连接)
#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
  Wire.begin();//初始化IIC连接，加入IIC总线
  Wire.setClock(400000); // IIC总线时钟频率400kHz
#elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
  Fastwire::setup(400, true);
#endif

  Serial.begin(115200);//初始化串口，波特率为：115200bps
  while (!Serial); //等待串口初始化成功

  Serial.println(F("Initializing I2C devices..."));//显示正在初始化IIC设备
  mpu.initialize();//MPU初始化


  // 加载、配置DMP
  Serial.println(F("Initializing DMP..."));//显示正在初始化DMP
  devStatus = mpu.dmpInitialize();//DMP初始化，并返回状态值

  // 给定陀螺仪偏移量
  mpu.setXGyroOffset(220);
  mpu.setYGyroOffset(76);
  mpu.setZGyroOffset(-85);
  mpu.setZAccelOffset(1788); // 出厂默认值1788

  // 设备正常运行
  if (devStatus == 0) {
    // 产生偏移，校准MPU6050
    mpu.CalibrateAccel(6);
    mpu.CalibrateGyro(6);
    mpu.PrintActiveOffsets();
    // 打开DMP, DMP准备好
    Serial.println(F("Enabling DMP..."));
    mpu.setDMPEnabled(true);

    // 使能中断检测
    Serial.print(F("Enabling interrupt detection (Arduino external interrupt "));
    Serial.print(digitalPinToInterrupt(INTERRUPT_PIN));
    Serial.println(F(")..."));
    attachInterrupt(digitalPinToInterrupt(INTERRUPT_PIN), dmpDataReady, RISING);
    mpuIntStatus = mpu.getIntStatus();

    // 设置DMP准备好标志
    Serial.println(F("DMP ready! Waiting for first interrupt..."));
    dmpReady = true;

    // 获取DMP数据包大小
    packetSize = mpu.dmpGetFIFOPacketSize();
  } else {
    // 1 表示初始化内存失败
    // 2 表示DMP配置更新失败
    // (if it's going to break, usually the code will be 1)
    Serial.print(F("DMP Initialization failed (code "));
    Serial.print(devStatus);
    Serial.println(F(")"));
  }
  //for (int i = 0; i < 8; i++)rotate(cube[i], 0.1, 0.1, 0.1); //旋转每个点

}

void loop() {
  // 若DMP未准备好,直接返回
  if (!dmpReady) return;
  // 读取陀螺仪数据
  if (mpu.dmpGetCurrentFIFOPacket(fifoBuffer)) { // 获取最新数据包
    //陀螺仪数据
    mpu.dmpGetQuaternion(&q, fifoBuffer);//读取四元数
    mpu.dmpGetGravity(&gravity, &q);//读取重力矢量
    mpu.dmpGetYawPitchRoll(ypr, &q, &gravity);//读取航向角、俯仰角、横滚角
    // 计算欧拉角
    am_x = ypr[0] * 180 / M_PI;
    am_y = ypr[1] * 180 / M_PI;
    am_z = ypr[2] * 180 / M_PI;
     // 串口监视器显示欧拉角
    Serial.print("ypr\t");
    Serial.print(am_x);
    Serial.print("\t");
    Serial.print(am_y);
    Serial.print("\t");
    Serial.println(am_z);
    //计算旋转立方体矩阵
    for (int i = 0; i < 8; i++)rotate(cube[i], (m_z - am_z) * 0.1, (m_y - am_y) * 0.1 , (m_x - am_x) * 0.1); //旋转每个点am_z - m_z
     //将欧拉角暂存至缓冲区
    if (m_x != am_x)
      m_x = am_x;
    if (m_y != am_y)
      m_y = am_y;
    if (m_z != am_z)
      m_z = am_z;
  }

  //OLED屏上显示欧拉角
  u8g2.clearBuffer();          // 清显示屏缓冲区
  u8g2.setFont(u8g2_font_6x10_mf  ); // 设置字体
  u8g2.setCursor(0, 10);
  //安装时陀螺仪的x方向和y方向互换了
  u8g2.print("x:");
  u8g2.print(am_y);

  u8g2.setCursor(0, 20);
  u8g2.print("y:");
  u8g2.print(am_z);

  u8g2.setCursor(0, 30);
  u8g2.print("z:");
  u8g2.print(am_x);

  //绘制立方体
  for (int i = 0; i < 24; i += 2) { 
    u8g2.drawLine(64 + cube[lineid[i] - 1][0], 32 + cube[lineid[i] - 1][1], 64 + cube[lineid[i + 1] - 1][0], 32 + cube[lineid[i + 1] - 1][1]);
  }


  //按下KEY2键，云台以启动时位置为零点进行自稳追踪
  if (digitalRead(KEY2) == HIGH)
  {
    delay(100);
    //舵机角度校零
    if (digitalRead(KEY2) == HIGH)
    {
      dj_qiy = !dj_qiy;//云台舵机启动控制电平翻转，再按KEY2键，退出云台自稳控制。
      //赋舵机零点参考值
      dj_x = am_x;
      dj_y = am_y;
    }
  }
  //按下KEY3键，云台以当前位姿为零点进行自稳追踪
  if (dj_qiy)
  {
    //舵机角度校零
    if (digitalRead(KEY3) == HIGH)
    {
      delay(100);
      if (digitalRead(KEY3) == HIGH)
      {
        //以陀螺仪当前位姿为参考零点
        dj_x = am_x;
        dj_y = am_y;
      }
    }
    myservo1.write(180 - ((dj_x - am_x) + 90));        // 控制舵机1旋转
    myservo2.write(180 - ((dj_y - am_y) + 90));        // 控制舵机2旋转
    u8g2.setCursor(0, 60);

    u8g2.print(180 - ((dj_x - am_x) + 90));//显示舵机1旋转角度
    u8g2.print(" / ");
    u8g2.print(180 - ((dj_y - am_y) + 90));//显示舵机2旋转角度

  }
  u8g2.sendBuffer();          // 发送缓冲区数据至显示器，发刷新消息

}
