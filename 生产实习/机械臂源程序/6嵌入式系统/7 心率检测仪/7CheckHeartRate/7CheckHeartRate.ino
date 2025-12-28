#include <Arduino.h>
#include <U8g2lib.h>

#ifdef U8X8_HAVE_HW_SPI
#include <SPI.h>
#endif
#ifdef U8X8_HAVE_HW_I2C
#include <Wire.h>
#endif
U8G2_SH1106_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, /* reset=*/ U8X8_PIN_NONE);
//选择1.3寸SH1106 OLED显示屏
#include <Wire.h>
#include "MAX30105.h" 
#include "heartRate.h" //心率计算算法
MAX30105 particleSensor;
const byte RATE_SIZE = 4; //定义多少次心率数据取平均值，默认为4次
byte rates[RATE_SIZE]; //用于存放心率数据
byte rateSpot = 0;
long lastBeat = 0; //存放上次心跳发生的时间
float beatsPerMinute;//一次心率值
int beatAvg;//心率平均值
int js = 10;
const unsigned char co4[] U8X8_PROGMEM = {
  /*--  调入了一幅图像：C:\Users\ADMIN\Desktop\i-心率.bmp  --*/
  /*--  宽度x高度=32x32  --*/
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xC0, 0x07, 0xE0, 0x03, 0xF0, 0x1E, 0x78, 0x0F,
  0x18, 0x30, 0x0C, 0x18, 0x0C, 0x60, 0x06, 0x30, 0x06, 0xC0, 0x03, 0x60, 0x02, 0x80, 0x21, 0x40,
  0x02, 0x80, 0x21, 0x40, 0x02, 0x00, 0x70, 0xC0, 0x03, 0x00, 0x70, 0xC0, 0x02, 0x00, 0x58, 0xC0,
  0x02, 0x60, 0x58, 0x40, 0x06, 0x70, 0xC8, 0x40, 0xFE, 0xD3, 0x8C, 0x7F, 0xFC, 0xDB, 0x8C, 0x3F,
  0x18, 0x8E, 0x04, 0x18, 0x30, 0x8C, 0x07, 0x0C, 0x60, 0x80, 0x03, 0x06, 0xC0, 0x00, 0x03, 0x03,
  0x80, 0x01, 0x83, 0x01, 0x00, 0x03, 0xC0, 0x00, 0x00, 0x06, 0x60, 0x00, 0x00, 0x0C, 0x30, 0x00,
  0x00, 0x18, 0x18, 0x00, 0x00, 0x30, 0x0C, 0x00, 0x00, 0x60, 0x06, 0x00, 0x00, 0xC0, 0x03, 0x00,
  0x00, 0x80, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,

};
void setup() {
  u8g2.begin();//构造u8g2模式：初始化显示器，重置清屏，唤醒屏幕

  // 初始化心率传感器
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) //默认IIC 通讯, 通讯频率400kHz
  {
   
    u8g2.clearBuffer();          // 清除显示器缓冲区
    u8g2.setFont(u8g2_font_ncenB08_tr); // 选择合适的字体
    u8g2.drawStr(0, 10, "MAX30102"); // 绘制文本字符“MAX30102”
    u8g2.sendBuffer();          // 显示缓冲区数据
    delay(2000);
  }
  

  particleSensor.setup(); //配置心率传感器参数
  particleSensor.setPulseAmplitudeRed(0x0A); // 红色发光二极管设为低电平，表示传感器正在运行
  particleSensor.setPulseAmplitudeGreen(0); //绿灯熄灭
  int js = 0;// put your setup code here, to run once:

}

void loop() {
  long irValue = particleSensor.getIR();//读取心率传感器数据

  if (checkForBeat(irValue) == true)
  {
    //检测到一次心跳
    long delta = millis() - lastBeat;//计算两次心跳的时间差
    lastBeat = millis();//保存现在的时间至lastBeat变量
    beatsPerMinute = 60 / (delta / 1000.0);//根据两次心跳的时间差计算心率值

    if (beatsPerMinute < 255 && beatsPerMinute > 20)
    {
       //小于20BPM，大于255BPM，视为无效数据
      rates[rateSpot++] = (byte)beatsPerMinute; //将心跳数据存入缓冲区以便求平均值
      rateSpot %= RATE_SIZE; //循环存储
      //取平均值
      beatAvg = 0;
      for (byte x = 0 ; x < RATE_SIZE ; x++)
        beatAvg += rates[x];
      beatAvg /= RATE_SIZE;
    }
  }

  js++;
  if (js > 100)
  {
    js = 0;
    u8g2.clearBuffer();          // 清除显示屏缓冲区
    u8g2.drawXBMP(16, 16, 32, 32, co4);//显示心率检测仪图标
    u8g2.setFont(u8g2_font_7Segments_26x42_mn); // 选择字体
    u8g2.setCursor(55, 50);
    u8g2.print(beatAvg);//显示心率值
    u8g2.setFont(u8g2_font_6x10_mf  ); // 选择字体

    u8g2.setCursor(0, 64);
    u8g2.print("IR=");
    u8g2.print(irValue);
    u8g2.print(", BPM=");
    u8g2.print(beatsPerMinute);

    u8g2.sendBuffer();          // 将缓冲区内容发送到显示器，发送刷新消息
  }
  if (irValue < 50000)
  {
    u8g2.setFont(u8g2_font_6x10_mf  ); // 选择字体
    u8g2.setCursor(0, 64);
    u8g2.print(" No finger? ");
    u8g2.sendBuffer();          //将缓冲区内容发送到显示器，发送刷新消息
  }
}
