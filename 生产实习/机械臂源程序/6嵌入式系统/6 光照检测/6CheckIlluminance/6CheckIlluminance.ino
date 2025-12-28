void setup()
{
  Serial.begin(9600);//初始化串口，设置波特率9600
}
void loop()
{
  int val;
  val = analogRead(5); //从ADC5引脚读取光照数据
  Serial.println(val, DEC); //输出光照数据至串口监视窗口显示
  delay(100);
}
