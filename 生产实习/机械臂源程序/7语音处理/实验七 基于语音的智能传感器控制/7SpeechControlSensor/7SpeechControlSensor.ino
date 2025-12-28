#include <Arduino.h>
#include <U8g2lib.h>

#ifdef U8X8_HAVE_HW_SPI
#include <SPI.h>
#endif
#ifdef U8X8_HAVE_HW_I2C
#include <Wire.h>
#endif
U8G2_SH1106_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, /* reset=*/ U8X8_PIN_NONE);
///////////////////////////////////////////////////////////////////////////////////////
#include <dht11.h>
dht11 DHT;
#define DHT11_PIN 23
///////////////////////////////////////////////////////////////////////////////////////
int LED1 = 11;
int FAN = 10;
int DSP = 0;
const unsigned char cz8[] U8X8_PROGMEM = {
  /*--  调入了一幅图像：C:\Users\ADMIN\Desktop\语音控制.bmp  --*/
  /*--  宽度x高度=56x16  --*/
  0xF2, 0x1F, 0x08, 0x40, 0x08, 0x40, 0x20, 0x84, 0x00, 0x10, 0x40, 0x10, 0x48, 0x20, 0x84, 0x80,
  0xFF, 0x43, 0xFE, 0xF9, 0x2B, 0xE0, 0x0F, 0x82, 0xF0, 0x02, 0x45, 0x28, 0x40, 0x08, 0x44, 0x40,
  0x48, 0x40, 0x28, 0x47, 0xC8, 0xFF, 0x47, 0x84, 0xFC, 0x2B, 0xF4, 0x1F, 0x00, 0x40, 0x02, 0x41,
  0x28, 0x04, 0x00, 0xFF, 0xC1, 0x00, 0x40, 0x28, 0x04, 0x00, 0x01, 0x71, 0xFC, 0xF8, 0x2B, 0xE4,
  0x0F, 0x01, 0x41, 0x10, 0x48, 0x2A, 0x34, 0x08, 0xFF, 0x41, 0x10, 0x48, 0x22, 0x2C, 0x08, 0x01,
  0x41, 0x10, 0x48, 0x22, 0xE4, 0x0F, 0x01, 0x41, 0x10, 0x48, 0x23, 0x20, 0x08, 0xFF, 0x71, 0xFE,
  0x41, 0x38, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
};
void setup() {
  u8g2.begin();
  pinMode(LED1, OUTPUT);
  Serial.begin(115200); // 打开串口，设置波特率：9600 bps
  pinMode(FAN, OUTPUT);
  u8g2.clearBuffer();
  u8g2.drawXBMP(0, 0, 56, 16, cz8);
  u8g2.sendBuffer();
}

void loop() {
  if (Serial.available() > 0)
  {
    int REED = Serial.read();   // 读取NX处理器串口转发过来的语音指令
    if (REED == 'A')    // 指令“A”
    {
      digitalWrite(LED1, HIGH);   // 开灯
    }
    else if (REED == 'B')   // 指令“B”
    {
      digitalWrite(LED1, LOW);   // 关灯
    }
    else if (REED == 'C')   // 指令“C”
    {
      analogWrite(FAN, 255);    // 开风扇
    }
    else if (REED == 'D')   // 指令“D”
    {
      analogWrite(FAN, 0);    // 关风扇
    }
    else if (REED == 'E')   // 指令“E”——显示温湿度指令
    {
      DSP = 1;
    }
  }

// 读取温湿度数据，并显示
  if (DSP == 1)
  {
    DHT.read(DHT11_PIN);    // 读温湿度数据
    u8g2.clearBuffer();
    u8g2.setFont(u8g2_font_ncenB14_tr);
    u8g2.drawXBMP(0, 0, 56, 16, cz8);   // 显示语音控制图标
    u8g2.setCursor(0, 40);    //设置光标处
    u8g2.print("TEM:");
    u8g2.print(DHT.temperature);    // 显示温度
    u8g2.setCursor(0, 64);    //设置光标处
    u8g2.print("HUM:");
    u8g2.print(DHT.humidity);   // 显示湿度
    u8g2.sendBuffer();
  }
}
