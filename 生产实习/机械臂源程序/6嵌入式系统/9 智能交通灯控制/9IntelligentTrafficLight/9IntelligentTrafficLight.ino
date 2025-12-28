han#include <Arduino.h>
#include <U8g2lib.h>
#ifdef U8X8_HAVE_HW_SPI
#include <SPI.h>
#endif
#ifdef U8X8_HAVE_HW_I2C
#include <Wire.h>
#endif
//选择1.3寸SH1106 OLED显示屏
U8G2_SH1106_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, /* reset=*/ U8X8_PIN_NONE);
# include "DFRobot_LedDisplayModule.h"
DFRobot_LedDisplayModule LED(Wire, 0x48);//定义数码管IIC端口地址：0x48
int js = 10;//秒计数器
int sunxu = 0;//交通灯状态序号，0：红灯，1：绿灯，2：黄灯
int LED1 = 11;//定义红灯LED1引脚11号
int LED2 = 12;//定义黄灯LED2引脚12号
int LED3 = 13;//定义绿灯LED3引脚13号
const unsigned char cz1[] U8X8_PROGMEM = {
  /*--  调入了一幅图像：C:\Users\ADMIN\Desktop\红绿灯.bmp  --*/
  /*--  宽度x高度=42x16  --*/
  /*--  宽度不是8的倍数，现调整为：宽度x高度=48x16  --*/
  0x04, 0x00, 0x01, 0x80, 0x00, 0x00, 0x04, 0x00, 0xF9, 0x81, 0xFC, 0x01, 0xD2, 0x8F, 0x00, 0x81,
  0x40, 0x00, 0x12, 0x81, 0xF2, 0xA1, 0x42, 0x00, 0x0F, 0xC1, 0x03, 0xA1, 0x42, 0x00, 0x08, 0x01,
  0xF9, 0xA7, 0x41, 0x00, 0x04, 0x81, 0x40, 0x90, 0x40, 0x00, 0x02, 0xC1, 0x4B, 0x82, 0x40, 0x00,
  0x1F, 0x01, 0x50, 0x81, 0x40, 0x00, 0x00, 0x01, 0xE0, 0x80, 0x40, 0x00, 0x00, 0x01, 0x53, 0x41,
  0x41, 0x00, 0x18, 0xC1, 0x4C, 0x46, 0x42, 0x00, 0x07, 0x01, 0x40, 0x20, 0x42, 0x00, 0xE0, 0x1F,
  0x70, 0x10, 0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
};
void setup() {
  u8g2.begin();//构造u8g2模式：初始化显示器，重置清屏，唤醒屏幕
  pinMode(LED1, OUTPUT);//设置LED1引脚为输出引脚
  pinMode(LED2, OUTPUT);//设置LED2引脚为输出引脚
  pinMode(LED3, OUTPUT);//设置LED3引脚为输出引脚
  // 初始化数码管，显示"H", "A", "L", "O"
  if (LED.begin4() != 0)
  {
    Serial.println("Failed to initialize the chip , please confirm the chip connection!");
    delay(1000);
  }
  LED.setDisplayArea4(1, 2, 3, 4);
  LED.print4("H", "A", "L", "O");//4个数码管分别显示"H", "A", "L", "O"。
  delay(1000);
}

void loop() {
  if (sunxu == 0)
  {
    digitalWrite(12, LOW);//黄灯灭
    digitalWrite(11, HIGH);//红灯亮
    if (js <= 0)
    {
      js = 5;
      sunxu = 1;
      digitalWrite(11, LOW);//红灯灭
    }
  }
  if (sunxu == 1)
  {
    digitalWrite(13, HIGH);//绿灯亮
    if (js <= 0)
    {
      js = 3;
      sunxu = 2;
      digitalWrite(13, LOW);//绿灯灭
    }
  }
  if (sunxu == 2)
  {
    digitalWrite(12, HIGH);//黄灯亮

    if (js < 1)
    {
      js = 10;
      sunxu = 0;
      digitalWrite(11, HIGH);//红灯亮
      digitalWrite(12, LOW);//黄灯灭
    }
  }
  u8g2.clearBuffer();          // 清显示缓冲区
  u8g2.drawXBMP(0, 0, 48, 16, cz1);//显示红绿灯图标
  u8g2.setFont(u8g2_font_7Segments_26x42_mn); // 设置字体
  u8g2.setCursor(55, 50);//设置OLED显示屏光标位置
  u8g2.print(js);//OLED屏显示计数器
  if (js > 9)
  {
    LED.setDisplayArea4(3, 4); //设置显示区为3、4号数码管
    LED.print4(js);//秒计数器小于等于9，则4号数码管显示计时时间
  }
  else
  {
    LED.setDisplayArea4(4);//设置显示区为4号数码管
    LED.print4(js);//秒计数器小于等于9，则4号数码管显示计时时间
  }
  u8g2.sendBuffer();//将缓冲区数据发送给显示器，发刷新消息         
  delay(1000);
  js--;
}
