#include <Arduino.h>
#include <SD.h>
#include <SPI.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>
#include <stdint.h>


int parse_int(const char *buf, const char *label);
char *parse_quoted_text(const char *buf, const char *label);

#define CS_PIN 5          // Укажите используемый CS-пин
#define MAX_FILE_SIZE 2048 // Максимальный размер файла (2 КБ)
File myFile;


void setup() {
  Serial.begin(115200);
  while (!Serial); // Ожидание подключения Serial

  // Инициализация SD-карты
  Serial.println("Инициализация SD карты...");
  if (!SD.begin(CS_PIN)) {
    Serial.println("Ошибка инициализации SD!");
    return;
  }
  Serial.println("SD инициализирована.");

  // Открытие файла test.bin
  myFile = SD.open("/test.bin");
  if (!myFile) {
    Serial.println("Ошибка открытия test.bin");
    return;
  }

  // Проверка размера файла
  size_t size = myFile.size();
  if (size == 0 || size > MAX_FILE_SIZE) {
    Serial.println("Некорректный размер файла");
    myFile.close();
    return;
  }

  // Чтение файла в буфер
  char *buf = (char *)malloc(size + 1);
  if (!buf) {
    Serial.println("Не удалось выделить память");
    myFile.close();
    return;
  }
  myFile.readBytes(buf, size);
  buf[size] = '\0';
  myFile.close();

  // Парсинг данных
  int id = parse_int(buf, "ID=");
  int type = parse_int(buf, "TYPE=");
  int speed = parse_int(buf, "SPEED=");
  
  Serial.print("ID = "); Serial.println(id);
  Serial.print("TYPE = "); Serial.println(type);
  Serial.print("SPEED = "); Serial.println(speed);

  char *text = parse_quoted_text(buf, "TEXT=");
  if (text) {
    Serial.print("TEXT = \""); Serial.print(text); Serial.println("\"");
    free(text);
  } else {
    Serial.println("TEXT не найден");
  }

  free(buf);
}

void loop() {}


int parse_int(const char *buf, const char *label) {
  char *p = strstr(buf, label);
  if (!p) return -1;
  p += strlen(label);
  return (int)strtol(p, NULL, 10);
}

char *parse_quoted_text(const char *buf, const char *label) {
  char *p = strstr(buf, label);
  if (!p) return NULL;
  p = strchr(p, '"');
  if (!p) return NULL;
  char *q = strchr(p + 1, '"');
  if (!q) return NULL;
  size_t len = q - p - 1;
  char *out = (char *)malloc(len + 1);
  if (!out) return NULL;
  memcpy(out, p + 1, len);
  out[len] = '\0';
  return out;
}