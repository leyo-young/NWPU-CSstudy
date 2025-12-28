
#include <Arduino.h>
#include <U8g2lib.h>

#ifdef U8X8_HAVE_HW_SPI
#include <SPI.h>
#endif
#ifdef U8X8_HAVE_HW_I2C
#include <Wire.h>
#endif

U8G2_SH1106_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, /* reset=*/ U8X8_PIN_NONE);//选择1.3寸SH1106 OLED显示屏
void setup(void) {
  u8g2.begin();//构造u8g2模式：初始化显示器，重置清屏，唤醒屏幕
}

void loop(void) {
  u8g2.clearBuffer();         // 清缓冲区
  u8g2.setFont(u8g2_font_ncenB08_tr); // 设置字体
  u8g2.drawStr(0,10,"Hello World!");  // 绘制字符串“Hello World”
  u8g2.sendBuffer();          // 将缓冲区数据发送给示显器，发刷新消息
  delay(1000);    
}
