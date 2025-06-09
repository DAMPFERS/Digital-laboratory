#include <Arduino.h>
#include <Wire.h>
#include <stdint.h>

// Настройки I2C для ESP32
#define I2C_SDA 21
#define I2C_SCL 22

// Адреса PCF8575
#define U1_ADDR 0x21 // Кнопки
#define U2_ADDR 0x20 // Генераторы

// Константы генераторов
#define OUT_OFF 0x00FF
#define PERIOD 2000

// Состояния системы
uint16_t last_buttonstate = 0;
uint16_t buttonstate = 0;
uint16_t gen_state = 0;
unsigned long period = 0;


uint16_t update_state();
void pf575_write(uint16_t data, uint8_t addr);
uint16_t pcf8575_read(uint8_t addr);

void setup() {
  Wire.begin(I2C_SDA, I2C_SCL); // Инициализация I2C
  Serial.begin(115200);
  
  // Инициализация PCF8575
  pf575_write(OUT_OFF, U2_ADDR); // Выключить все генераторы
  pf575_write(0xFFFF, U1_ADDR);  // Настройка входов кнопок
  
  Serial.println("System initialized");
}

void loop() {
  gen_state = update_state();
  pf575_write(gen_state, U2_ADDR);
  
  // Вывод состояния в Serial Monitor
  Serial.print("Current state: 0x");
  Serial.println(gen_state, HEX);
  
  delay(10);
}

// Функция обновления состояния
uint16_t update_state() {
  uint16_t new_state = gen_state;
  
  // Обработка периодических событий
  if(millis() - period > PERIOD) {
    period = millis();
    new_state ^= 0x00FF; // Инвертировать младшие 8 бит для меандра
  }

  // Чтение кнопок
  buttonstate = pcf8575_read(U1_ADDR);
  if(buttonstate != 0xFFFF) {
    if(buttonstate != last_buttonstate) {
      new_state = (~buttonstate) & 0x00FF; // Обновить состояние по кнопкам
      last_buttonstate = buttonstate;
    }
  }
  
  return new_state;
}

// Функции работы с PCF8575
void pf575_write(uint16_t data, uint8_t addr) {
  Wire.beginTransmission(addr);
  Wire.write(lowByte(data));
  Wire.write(highByte(data));
  Wire.endTransmission();
}

uint16_t pcf8575_read(uint8_t addr) {
  Wire.beginTransmission(addr);
  Wire.endTransmission();
  Wire.requestFrom(addr, (int)2);
  return Wire.read() | (Wire.read() << 8);
}