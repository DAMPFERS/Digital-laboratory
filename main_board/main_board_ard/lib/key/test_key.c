#include <Arduino.h>
#include <stdint.h>

#define KEY 13
#define CLOCK 14
#define LOAD 27

unsigned long period = 0;



void setup() {
  Serial.begin(115200);
  Serial.println("System initialized");

  pinMode(KEY, INPUT);
  pinMode(CLOCK, OUTPUT);
  pinMode(LOAD, OUTPUT);

  digitalWrite(CLOCK, HIGH);
}

void loop() {
  // Serial.println("0_o");
  // delay(1000);
  if (millis() - period > 50){
    unsigned char res = 0;

    digitalWrite(CLOCK, LOW);
    delay(2);
    digitalWrite(CLOCK, HIGH);
    for(char i = 0; i < 8; i++){
      res = res << 1;
      res |= digitalRead(KEY);

      digitalWrite(LOAD, HIGH);
      delay(2);
      digitalWrite(LOAD, LOW);
    }
    Serial.println(res, BIN);

    period = millis();
  }
  
}
