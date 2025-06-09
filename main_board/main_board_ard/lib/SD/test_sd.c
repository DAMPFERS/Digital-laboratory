#include <Arduino.h>
#include <stdint.h>
#include <SPI.h>
#include <SD.h>

// Настройка пинов для вашего SD-модуля
#define CS_PIN 5  // Укажите используемый CS-пин
float refresh_rate = 5000.0;

File myFile;

void setup() {
  Serial.begin(115200);
  pinMode(CS_PIN, OUTPUT);
  // SD.begin(CS_PIN, 1000000);
  // while (!Serial) {
    // ; // Ожидание инициализации последовательного порта
  // }

  Serial.print("\nИнициализация SD-карты...");

  if (!SD.begin(CS_PIN)) {
    Serial.println("Инициализация не удалась!");
    while (1);
  }
  Serial.println("Инициализация выполнена.");

  // Создание и запись в файл
  if (SD.exists("/test.txt")) {
    Serial.println("test.txt уже существует. Удаляем...");
    SD.remove("/test.txt");
  }

  myFile = SD.open("/test.txt", FILE_WRITE);
  
  if (myFile) {
    Serial.println("Запись в файл...");
    myFile.println("Тестирование SD-карты ESP32");
    myFile.println("Это тестовая запись");
    myFile.close();
    Serial.println("Запись завершена.");
  } else {
    Serial.println("Ошибка открытия файла для записи!");
  }

  // Чтение из файла
  myFile = SD.open("/test.txt");
  if (myFile) {
    Serial.println("\nСодержимое test.txt:");
    while (myFile.available()) {
      Serial.write(myFile.read());
    }
    myFile.close();
  } else {
    Serial.println("Ошибка открытия файла для чтения!");
  }
}

void loop() {
  // Ничего не делаем в цикле
}