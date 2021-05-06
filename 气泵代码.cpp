#include <Servo.h> 

Servo myservo0;
Servo myservo1;

 //创建气泵和电磁阀控制对象（Servo myservo0）为气泵 （ Servo myservo1）为电磁阀  
 
// 该变量用气泵电磁阀开关（0为关闭，180为开启）
unsigned char c;
void setup() 
{ 
  Serial.begin(9600);
  myservo0.attach(9);
  myservo1.attach(8);

  myservo0.write(0);  
  myservo1.write(0);  

// 代表气泵插9引脚，电磁阀插8引脚 arduino控制  
} 

void loop() 
{ 

if (Serial.available() > 0)//串口接收到数据
  {
    c = Serial.read();//获取串口接收到的数据
    //Serial.println(c);
    if (c == '0')
    {
     // Serial.println("get");
      myservo0.write(180);   
      myservo1.write(0);
    
    //此行代码表示气泵开，电磁阀关闭状态 
      delay(2000);                           
    // 表示此组动作运行时间3000毫秒，时间可以自由修改   
    
      myservo0.write(0);   
      myservo1.write(0);
    
    // 此行代码表示气泵关，电磁阀关闭状态，气泵已经吸附物品移动。此时也可以按照实际需求开启或者关闭气泵。  
      
    }else if(c == '1'){
        myservo0.write(0);   
        myservo1.write(180);
      
      // 此行代码表示气泵关，电磁阀开启状态，物品脱离吸盘。 
        delay(800);                           
      //放下物品等待时间800毫秒，  时间可以自由修改  
      
        myservo0.write(0);   
        myservo1.write(0);
      
      // 此行代码表示气泵关，电磁阀关状态，运行完成结束。
     // Serial.println("put");
    }
  }
c='a';
  delay(100);
}