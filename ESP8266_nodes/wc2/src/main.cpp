#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#define RELAY_PIN D1
#define LED_PIN   LED_BUILTIN

const char* ssid = "Vinternal";
const char* password = "abcd123456";
const char* mqtt_server = "192.168.20.109";
const char* node_id = "wc2";
const char* node_type = "male";
const char* room_name = "Room 2";

WiFiClient espClient;
PubSubClient client(espClient);

void maximize_wifi_power() {
#if defined(ESP8266)
  #if defined(ARDUINO_ESP8266_MAJOR) && ARDUINO_ESP8266_MAJOR >= 3
    WiFi.setOutputPower(20.5); // Max power in dBm for ESP8266 core 3.x+
  #else
    WiFi.setTxPower(WIFI_POWER_19_5dBm); // Max power for older core
  #endif
#endif
}

unsigned long lastStatusTime = 0;
unsigned long relayOffTime = 0;
bool relayActive = false;

void setup_wifi() {
  delay(10);
  Serial.print("[wc2] Connecting to WiFi");
  WiFi.begin(ssid, password);
  int retry = 0;
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);
  while (WiFi.status() != WL_CONNECTED) {
    delay(250);
    digitalWrite(LED_PIN, !digitalRead(LED_PIN)); // Flash LED
    Serial.print(".");
    retry++;
    if (retry > 80) { // 80 x 250ms = 20s
      digitalWrite(LED_PIN, HIGH);
      Serial.println("\n[wc2] WiFi connection failed!");
      return;
    }
  }
  digitalWrite(LED_PIN, HIGH); // LED steady ON after connect
  Serial.println("\n[wc2] WiFi connected!");
  Serial.print("[wc2] IP: ");
  Serial.println(WiFi.localIP());
  Serial.print("[wc2] WiFi RSSI: ");
  Serial.println(WiFi.RSSI()); // Returns signal strength in dBm
}

void publish_status() {
  JsonDocument doc;
  doc["node_id"] = node_id;
  doc["node_type"] = node_type;
  doc["room_name"] = room_name;
  doc["status"] = "online";
  doc["wifi_connected"] = (WiFi.status() == WL_CONNECTED);
  doc["relay_active"] = relayActive;
  doc["timestamp"] = millis() / 1000;
  char buf[256];
  size_t n = serializeJson(doc, buf);
  String topic = String("wc/") + node_id + "/status";
  client.publish(topic.c_str(), buf, n);
  Serial.print("[wc2] Status published, RSSI: ");
  Serial.println(WiFi.RSSI());
}

void publish_response(const char* action, bool success, const char* message) {
  JsonDocument doc;
  doc["node_id"] = node_id;
  doc["action"] = action;
  doc["success"] = success;
  doc["message"] = message;
  doc["timestamp"] = millis() / 1000;
  char buf[256];
  size_t n = serializeJson(doc, buf);
  String topic = String("wc/") + node_id + "/response";
  client.publish(topic.c_str(), buf, n);
  Serial.print("[wc2] Response published: ");
  Serial.println(action);
}

void blink_led_4s() {
  Serial.println("[wc2] Blinking LED for 4 seconds...");
  for (int i = 0; i < 20; i++) {
    digitalWrite(LED_PIN, LOW);
    delay(100);
    digitalWrite(LED_PIN, HIGH);
    delay(100);
  }
  digitalWrite(LED_PIN, HIGH);
  Serial.println("[wc2] LED blinking done");
}

void stop_relay() {
  digitalWrite(RELAY_PIN, LOW);
  relayActive = false;
  digitalWrite(LED_PIN, HIGH);
  publish_response("stop", true, "Relay deactivated");
  Serial.println("[wc2] Relay stopped");
}

void execute_flush() {
  digitalWrite(RELAY_PIN, HIGH);
  relayActive = true;
  digitalWrite(LED_PIN, LOW);
  relayOffTime = millis() + 5000;
  publish_response("flush", true, "Flush executed, LED blinking 4s");
  Serial.println("[wc2] FLUSH command received!");
  blink_led_4s();
}

void callback(char* topic, byte* payload, unsigned int length) {
  String msg;
  for (unsigned int i = 0; i < length; i++) msg += (char)payload[i];
  String action = msg;
  Serial.print("[wc2] MQTT message received: ");
  Serial.println(msg);
  JsonDocument doc;
  DeserializationError err = deserializeJson(doc, msg);
  if (!err) {
    if (doc["action"].is<String>()) action = doc["action"].as<String>();
    Serial.print("[wc2] Parsed action: ");
    Serial.println(action);
  }
  action.trim();
  if (action == "flush" || action == "on" || action == "activate") {
    execute_flush();
  } else if (action == "status" || action == "ping") {
    publish_status();
    Serial.println("[wc2] STATUS command received!");
  } else if (action == "off" || action == "stop") {
    stop_relay();
    Serial.println("[wc2] STOP command received!");
  } else {
    publish_response(action.c_str(), false, "Unknown action");
    Serial.print("[wc2] Unknown action: ");
    Serial.println(action);
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.println("[wc2] Attempting MQTT connection...");
    if (client.connect(node_id)) {
      String topic = String("wc/") + node_id + "/command";
      client.subscribe(topic.c_str());
      Serial.print("[wc2] Subscribed to topic: ");
      Serial.println(topic);
    } else {
      Serial.println("[wc2] MQTT connection failed, retrying...");
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  delay(100);
  Serial.println("[wc2] Starting node...");
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);
  digitalWrite(LED_PIN, HIGH);
  maximize_wifi_power();
  setup_wifi();
  Serial.println("[wc2] WiFi connected!");
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  // Test LED startup
  Serial.println("[wc2] Testing LED...");
  for (int i = 0; i < 3; i++) {
    digitalWrite(LED_PIN, LOW); delay(300);
    digitalWrite(LED_PIN, HIGH); delay(300);
  }
  Serial.println("[wc2] LED test complete");
  publish_status();
  Serial.println("[wc2] Node ready!");
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();
  unsigned long now = millis();
  // Tự động tắt relay sau 5s
  if (relayActive && now > relayOffTime) {
    stop_relay();
  }
  // Định kỳ publish status mỗi 10s
  if (now - lastStatusTime > 10000) {
    publish_status();
    lastStatusTime = now;
  }
}
