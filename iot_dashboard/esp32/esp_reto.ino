#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>
#include "DHT.h"

// -------------------- CONFIG --------------------
#define WIFI_SSID     "Tec-IoT"
#define WIFI_PASSWORD "spotless.magnetic.bridge"

#define MQTT_SERVER   "10.25.15.228"
#define MQTT_PORT     1883

#define DHTPIN 4
#define DHTTYPE DHT11

// Pines de los 3 sensores de suelo
#define SOIL1_PIN 34
#define SOIL2_PIN 35
#define SOIL3_PIN 32

// Pin del fotorresistor
#define LDR_PIN 33

// Telegram Bot details
String BOTtoken = "7739412640:AAElkEqytyy8Bi_LIEaBQV-vlYap53SbJZw";
String chatID   = "7266511122";

// MQTT objects
WiFiClient espClient;
PubSubClient client(espClient);
DHT dht(DHTPIN, DHTTYPE);

// Timers
unsigned long lastMsg = 0;
const long interval = 600000;  // 10 min en milisegundos
unsigned long lastMQTTok = 0;
const long mqttTimeout = 6000; // 60s

// -------------------- FUNCTIONS --------------------
void sendTelegramMessage(String message) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = "https://api.telegram.org/bot" + BOTtoken +
                 "/sendMessage?chat_id=" + chatID +
                 "&text=" + message;

    http.begin(url);
    int httpResponseCode = http.GET();

    if (httpResponseCode > 0) {
      Serial.print("➡️ Sent Telegram: ");
      Serial.println(message);
    } else {
      Serial.print("❌ Telegram error, code: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  }
}

void connectWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ WiFi connected");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void reconnectMQTT() {
  if (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect("ESP32Client")) {
      Serial.println("✅ MQTT connected");
      lastMQTTok = millis();
    } else {
      Serial.print("❌ MQTT connect failed, rc=");
      Serial.println(client.state());
    }
  }
}

// -------------------- SETUP --------------------
void setup() {
  Serial.begin(115200);
  dht.begin();

  connectWiFi();
  client.setServer(MQTT_SERVER, MQTT_PORT);

  sendTelegramMessage("🤖 ESP32 started and monitoring sensors...");
}

// -------------------- LOOP --------------------
void loop() {
  if (client.connected()) {
    client.loop();
    lastMQTTok = millis();
  } else {
    reconnectMQTT();
  }

  if (!client.connected() && (millis() - lastMQTTok > mqttTimeout)) {
    sendTelegramMessage("⚠️ ESP32 lost MQTT connection for more than 1 minute!");
    lastMQTTok = millis();
  }

  unsigned long now = millis();
  if (now - lastMsg > interval) {
    lastMsg = now;

    // --- DHT11 ---
    float h = dht.readHumidity();
    float t = dht.readTemperature();

    if (!isnan(h) && !isnan(t)) {
      char tempStr[16], humStr[16];
      dtostrf(t, 4, 2, tempStr);
      dtostrf(h, 4, 2, humStr);

      client.publish("sensors/temperature", tempStr);
      client.publish("sensors/humidity", humStr);

      Serial.printf("🌡️ Temp: %.2f °C | 💧 Hum: %.2f %%\n", t, h);
    } else {
      client.publish("errores", "DHT11 read failed");
      Serial.println("❌ Error: DHT11 read failed → published to errores");
    }

    // --- Soil sensors (3 promedio) ---
    int soil1 = analogRead(SOIL1_PIN);
    int soil2 = analogRead(SOIL2_PIN);
    int soil3 = analogRead(SOIL3_PIN);

    int soilAvgRaw = (soil1 + soil2 + soil3) / 3;
    int soilPercent = map(soilAvgRaw, 4095, 0, 100, 0);

    char soilStr[16];
    dtostrf(soilPercent, 4, 2, soilStr);
    client.publish("sensors/soil", soilStr);

    Serial.printf("🌱 Soil AVG: %d (raw) | %d %%\n", soilAvgRaw, soilPercent);

    // --- Fotorresistor ---
    int ldrValue = analogRead(LDR_PIN);
    int lightPercent = map(ldrValue, 0, 4095, 100, 0); // 0 oscuro - 100 luz máxima

    char ldrStr[16];
    dtostrf(lightPercent, 4, 2, ldrStr);
    client.publish("sensors/light", ldrStr);

    Serial.printf("💡 LDR: %d (raw) | %d %%\n", ldrValue, lightPercent);

    Serial.println("----------------------");
  }
}

