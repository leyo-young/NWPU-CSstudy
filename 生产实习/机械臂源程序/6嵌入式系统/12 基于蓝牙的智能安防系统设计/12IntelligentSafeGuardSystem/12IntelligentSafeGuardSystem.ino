#include <Arduino.h>
#include <U8g2lib.h>
#ifdef U8X8_HAVE_HW_SPI
#include <SPI.h>
#endif
#ifdef U8X8_HAVE_HW_I2C
#include <Wire.h>
#endif
//选择1.3寸SH1106 OLED显示屏
U8G2_SH1106_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, /* reset=*/ U8X8_PIN_NONE);
int zhuangtai = 0;//定义状态变量
int qt_zt = 140, hy_zt = 800;//定义气体和火焰安全值
int LED1 = 11;//定义灯LED1为11号引脚
int LED2 = 12;//定义灯LED2为12号引脚
int LED3 = 13;//定义灯LED3为13号引脚
int KEY1 = 4;//定义按键KEY1为4号引脚
int KEY2 = 5;//定义按键KEY2为5号引脚
int KEY3 = 6;//定义按键KEY3为6号引脚
int BEEP = 7;//定义蜂鸣器BEEP为7号引脚
int FAN = 10;//定义风扇FAN为10号引脚
int SENY = A11;
int LIANDU = A5;
int leida = 22;//定义人体雷达leida为22号引脚
int huoyan = A10;//定义火焰huoyan为A10引脚
int qiti = A9;//定义气体qiti为A9引脚
void setup() {
  Serial2.begin(9600);             //初始化串口2（蓝牙通信串口），并设置波特率为115200
  u8g2.begin();//构造u8g2模式：初始化显示器，重置清屏，唤醒屏幕
  pinMode(LED1, OUTPUT);//设置LED1引脚为输出模式
  pinMode(LED2, OUTPUT);//设置LED2引脚为输出模式
  pinMode(LED3, OUTPUT);//设置LED31引脚为输出模式
  pinMode(BEEP, OUTPUT);//设置BEEP引脚为输出模式
  pinMode(KEY1, INPUT);//设置KEY1引脚为输入模式
  pinMode(KEY2, INPUT);//设置KEY2引脚为输入模式
  pinMode(KEY3, INPUT);//设置KEY3引脚为输入模式
  pinMode(leida, INPUT);//设置leida引脚为输入模式
  Serial.begin(115200); // 初始化串口（串口监视窗口），并设置波特率为9600 
  pinMode(FAN, OUTPUT);//设置FAN引脚为输出模式
}

void loop() {
   //读取蓝牙通信模块数据
  if (Serial2.available() > 0)
  {
    int REED = Serial2.read();//读取蓝牙数据
    if (REED == 'A')
    {
      zhuangtai = 1;//设防：变量zhuangtai 置1
    }
    else if (REED == 'B')
    {
      zhuangtai = 0;//解防：变量zhuangtai清0
    }
  }
  int qt = analogRead(qiti);//读取气体传感器数据
  int hy = analogRead(huoyan);//读取火焰传感器数据
  u8g2.clearBuffer();          // 清显示器缓冲区
  u8g2.setFont(u8g2_font_6x10_mf  ); // 设置字体
  //人体雷达检测
  if (digitalRead(leida) == HIGH)
  {
    digitalWrite(LED1, HIGH);//检测到有人，点亮LED1灯
    u8g2.setFont(u8g2_font_streamline_interface_essential_id_t); //设置显示内置特殊图形
    u8g2.drawGlyph(72, 30, 0x0034);  //绘制人头形图标1
    u8g2.setFont(u8g2_font_6x10_mf  ); // 设置字体
  }
  else
  {
    digitalWrite(LED1, LOW);//没检测到人，熄灭LED1灯
  }
  if (zhuangtai)
  {
    u8g2.setFont(u8g2_font_streamline_interface_essential_key_lock_t);//设置显示内置特殊图形
    u8g2.drawGlyph(95, 30, 0x0036);  //绘制锁形图标2
    u8g2.setFont(u8g2_font_6x10_mf  ); // 设置字体
  }
  //设防状态下有人闯入或有气体泄露或有火焰
  if (hy < hy_zt || (digitalRead(leida) == HIGH && zhuangtai == 1) || qt > qt_zt)
  {
    digitalWrite(BEEP, HIGH);//蜂鸣器响
    u8g2.setFont(u8g2_font_streamline_interface_essential_circle_triangle_t); //设置显示内置特殊图形
    u8g2.drawGlyph(72, 60, 0x0030);  //绘制危险图标3
    u8g2.setFont(u8g2_font_6x10_mf  ); // 设置字体
  }
  else
  {
    digitalWrite(BEEP, LOW);//否则关闭蜂鸣器
  }
  //气体浓度大于安全值，有气体泄露
  if (qt > qt_zt)
  {
    analogWrite(FAN, 255);//开风扇
    u8g2.setFont(u8g2_font_streamline_interface_essential_action_t);//设置显示内置特殊图形    
    u8g2.drawGlyph(95, 60, 0x0036);  //绘制循环形图标4
    u8g2.setFont(u8g2_font_6x10_mf  ); // 设置字体
  }
  else
  {
    analogWrite(FAN, 0);//无气体泄露，关风扇
  }
  u8g2.setCursor(0, 30);
  u8g2.print("flame: ");
  u8g2.print(hy);//显示火焰传感器数据
  u8g2.setCursor(0, 40);
  u8g2.print("Gas: ");
  u8g2.print(qt);//显示气体传感器数据
  u8g2.sendBuffer();          // 将缓冲区数据发送给显示器，发刷新消息
}
