#include <Ultrasonic.h>

#include <Servo.h>

Servo myservo;
Ultrasonic ultrasonic(9, 8);

#define PARSE_AMOUNT 2
int intData[PARSE_AMOUNT];     // массив численных значений после парсинга
boolean recievedFlag;
boolean getStarted;
byte index;
long last_time = 0;
String string_convert = "";
void parsing() {
  if (Serial.available() > 0) {
    char incomingByte = Serial.read();        // обязательно ЧИТАЕМ входящий символ
    if (getStarted) {                         // если приняли начальный символ (парсинг разрешён)
      if (incomingByte != ' ' && incomingByte != ';') {   // если это не пробел И не конец
        string_convert += incomingByte;       // складываем в строку
      } else {                                // если это пробел или ; конец пакета
        intData[index] = string_convert.toInt();  // преобразуем строку в int и кладём в массив
        string_convert = "";                  // очищаем строку
        index++;                              // переходим к парсингу следующего элемента массива
      }
    }
    if (incomingByte == '$') {                // если это $
      getStarted = true;                      // поднимаем флаг, что можно парсить
      index = 0;                              // сбрасываем индекс
      string_convert = "";                    // очищаем строку
    }
    if (incomingByte == ';') {                // если таки приняли ; - конец парсинга
      getStarted = false;                     // сброс
      recievedFlag = true;                    // флаг на принятие
    }


  }
}

void setup() {
  Serial.begin(9600);
  Serial.println("Hello, im arduino");
  Serial.setTimeout(10);
  myservo.attach(4);
  pinMode(A3, 1);
  pinMode(A2, 1);
  pinMode(A1, INPUT);
  pinMode(3, 1);
  pinMode(5, 1);
  pinMode(6, 1);

}

void loop() {
  parsing();
  if (recievedFlag) {                           // если получены данные
    recievedFlag = false;
    switch (intData[0]) {
      case 1:
        digitalWrite(A3, intData[1]);
        break;
      case 2:
        digitalWrite(A2, intData[1]);
        break;
      case 3:
        digitalWrite(A1, intData[1]);
        break;
      case 4:
        analogWrite(3, intData[1]);
        break;
      case 5:
        analogWrite(5, intData[1]);
        break;
      case 6:
        analogWrite(6, intData[1]);
        break;
      case 10:
        myservo.write(intData[1]);
        break;
    }
  }
  if (millis() - last_time >= 50) {
    last_time = millis();
    Serial.print(5);
    Serial.print(" ");
    Serial.println(ultrasonic.read());
    Serial.print(6);
    Serial.print(" ");
    Serial.println(analogRead(A1));
    
  }
}
