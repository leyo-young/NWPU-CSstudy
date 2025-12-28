int leda = 22;//定义雷达信号为CPU 22号引脚
int ledPin =  13;//定义绿色指示灯LED3为CPU 13号引脚
void setup() {
  pinMode(ledPin, OUTPUT);
  pinMode(leda, INPUT);
}
void loop()
{
  if (digitalRead(leda) == HIGH) //读取人体雷达感应信号，若为高电平
  {
    digitalWrite(ledPin, HIGH);//点亮指示灯
  }
  else {
    digitalWrite(ledPin, LOW);//熄灭指示灯
  }
}
