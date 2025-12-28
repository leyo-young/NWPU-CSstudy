#include <Arduino.h>
#include <U8g2lib.h>

#ifdef U8X8_HAVE_HW_SPI
#include <SPI.h>
#endif
#ifdef U8X8_HAVE_HW_I2C
#include <Wire.h>
#endif
U8G2_SH1106_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, /* reset=*/ U8X8_PIN_NONE);    // 选择1.3寸SH1106 OLED显示屏
///////////////////////////////////////////////////////////////////////////////////////
#include <dht11.h>
dht11 DHT;
#define DHT11_PIN 23//温湿度引脚

String strword = "Hello World";//定义输出的字符串
void setup() {
Serial.begin(115200);//初始化串口,设置波特率9600
}
void loop() {
Serial.println(strword);//串口监视器显示字符
delay(1000);//延时1秒
}
