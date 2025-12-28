String strword = "Hello World";//定义输出的字符串
void setup() {
  Serial.begin(9600);//初始化串口，设置波特率9600
}
void loop() {
  Serial.println(strword);//串口监视器显示字符
  delay(1000);//延时1秒
}
