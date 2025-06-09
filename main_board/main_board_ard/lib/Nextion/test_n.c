#include <HardwareSerial.h>

// Конфигурация UART1 (пины по умолчанию: GPIO9 (RX1), GPIO10 (TX1))
// Проверьте распиновку вашей ESP32!
#define NEXTION_RX 16
#define NEXTION_TX 17

HardwareSerial nextionSerial(2); // UART2
const uint8_t endBytes[3] = {0xFF, 0xFF, 0xFF};

uint32_t readDataFromNextion();
void addPointToGraph(uint8_t id, uint8_t channel, uint8_t value);
void sendToNextion(const char* component, const char* value);

void setup() {
  Serial.begin(115200); // Для отладки
  nextionSerial.begin(9600, SERIAL_8N1, NEXTION_RX, NEXTION_TX);
  
  Serial.println("\nNextion ESP32 Initialization");
  delay(500); // Даем время для инициализации дисплея
}

void loop() {
  // Чтение данных от Nextion
  uint32_t receivedData = readDataFromNextion();
  if(receivedData != 0) {
    Serial.printf("Received data: 0x%08X\n", receivedData);
  }

  // Тестовые команды
  addPointToGraph(20, 1, 66);
  sendToNextion("page0.b0.txt", "hello");
  delay(100);
}

// Отправка команд на Nextion
void sendToNextion(const char* component, const char* value) {
  char buffer[64];
  snprintf(buffer, sizeof(buffer), "%s=\"%s\"", component, value);
  
  nextionSerial.print(buffer);
  nextionSerial.write(endBytes, sizeof(endBytes));
  
  Serial.printf("Sent: %s\n", buffer);
}

// Добавление точки на график

void addPointToGraph(uint8_t id, uint8_t channel, uint8_t value) {
  char command[16];
  snprintf(command, sizeof(command), "add %u,%u,%u", id, channel, value);
  
  nextionSerial.print(command);
  nextionSerial.write(endBytes, sizeof(endBytes));
  
  Serial.printf("Graph command: %s\n", command);
}

// Чтение данных от Nextion (улучшенная версия)
uint32_t readDataFromNextion() {
  static uint8_t buffer[7];
  uint32_t dataValue = 0;
  uint32_t controlBytes = 0;

  if(nextionSerial.available() >= 7) {
    nextionSerial.readBytes(buffer, 7);
    
    // Сборка данных
    for(uint8_t i = 0; i < 4; i++) {
      dataValue = (dataValue << 8) | buffer[i];
    }
    
    // Проверка контрольных байт
    for(uint8_t i = 4; i < 7; i++) {
      controlBytes = (controlBytes << 8) | buffer[i];
    }

    if(controlBytes == 0x00FFFFFF) {
      return dataValue;
    }
  }
  return 0;
}