#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

#define RELAY_PIN D1
#define LED_PIN   LED_BUILTIN

const char* ssid = "Michelle";
const char* password = "0908800130";
const char* mqtt_server = "192.168.1.181";
const char* node_id = "wc2";
const char* node_type = "male";
const char* room_name = "Room 2";

WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastStatusTime = 0;
unsigned long relayOffTime = 0;
bool relayActive = false;

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.printf("[%s] Connecting to WiFi...\n", node_id);
  WiFi.begin(ssid, password);
  int attempt = 0;
  while (WiFi.status() != WL_CONNECTED && attempt < 20) {
    delay(500);
    attempt++;
    Serial.printf("[%s] Connecting to WiFi... (%d/20)\n", node_id, attempt);
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("[%s] WiFi connected! IP: %s\n", node_id, WiFi.localIP().toString().c_str());
  } else {
    Serial.printf("[%s] WiFi connection failed\n", node_id);
  }
}

void publish_status() {
  StaticJsonDocument<256> doc;
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
  Serial.printf("[%s] Status published\n", node_id);
}

void publish_response(const char* action, bool success, const char* message) {
  StaticJsonDocument<256> doc;
  doc["node_id"] = node_id;
  doc["action"] = action;
  doc["success"] = success;
  doc["message"] = message;
  doc["timestamp"] = millis() / 1000;
  char buf[256];
  size_t n = serializeJson(doc, buf);
  String topic = String("wc/") + node_id + "/response";
  client.publish(topic.c_str(), buf, n);
}

void blink_led_4s() {
  Serial.printf("[%s] \xF0\x9F\x92\xA1 Starting 4-second LED blink sequence...\n", node_id); // 💡
  for (int i = 0; i < 20; i++) {
    digitalWrite(LED_PIN, LOW);
    Serial.printf("[%s] \xF0\x9F\x92\xA1 LED ON - blink %d/20\n", node_id, i+1);
    delay(100);
    digitalWrite(LED_PIN, HIGH);
    Serial.printf("[%s] \xF0\x9F\x92\xA1 LED OFF - blink %d/20\n", node_id, i+1);
    delay(100);
  }
  digitalWrite(LED_PIN, HIGH);
  Serial.printf("[%s] \xE2\x9C\x85 LED blinking completed - 4 seconds finished\n", node_id); // ✅
}

void stop_relay() {
  digitalWrite(RELAY_PIN, LOW);
  relayActive = false;
  digitalWrite(LED_PIN, HIGH);
  publish_response("stop", true, "Relay deactivated");
  Serial.printf("[%s] Relay stopped\n", node_id);
}

void execute_flush() {
  Serial.printf("[%s] \xF0\x9F\x9A\xBD FLUSH COMMAND PROCESSING STARTED!\n", node_id); // 🚽
  Serial.printf("[%s] \xF0\x9F\x94\xA7 Activating hardware...\n", node_id); // 🔧
  digitalWrite(RELAY_PIN, HIGH);
  relayActive = true;
  digitalWrite(LED_PIN, LOW);
  relayOffTime = millis() + 5000;
  publish_response("flush", true, "Flush executed, LED blinking 4s");
  Serial.printf("[%s] \xE2\x9C\x85 Relay activated: %d\n", node_id, digitalRead(RELAY_PIN)); // ✅
  blink_led_4s();
  Serial.printf("[%s] \xE2\x8F\xB0 5-second auto-off timer started\n", node_id); // ⏰
  Serial.printf("[%s] \xF0\x9F\x8E\x89 FLUSH COMMAND COMPLETED!\n", node_id); // 🎉
}

void callback(char* topic, byte* payload, unsigned int length) {
  String msg;
  for (unsigned int i = 0; i < length; i++) msg += (char)payload[i];
  String action = msg;
  Serial.printf("[%s] \xF0\x9F\x93\xA8 MQTT Message Received!\n", node_id); // 📨
  Serial.printf("[%s]    Topic: %s\n", node_id, topic);
  Serial.printf("[%s]    Message: %s\n", node_id, msg.c_str());
  // Try parse JSON
  StaticJsonDocument<128> doc;
  DeserializationError err = deserializeJson(doc, msg);
  if (!err) {
    if (doc.containsKey("action")) action = doc["action"].as<String>();
    Serial.printf("[%s]    Parsed Action: %s\n", node_id, action.c_str());
  } else {
    Serial.printf("[%s]    Using plain string action: %s\n", node_id, action.c_str());
  }
  action.trim();
  if (action == "flush" || action == "on" || action == "activate") {
    execute_flush();
  } else if (action == "status" || action == "ping") {
    Serial.printf("[%s] \xF0\x9F\x93\x8A STATUS REQUEST RECEIVED!\n", node_id); // 📊
    publish_status();
  } else if (action == "off" || action == "stop") {
    Serial.printf("[%s] \xF0\x9F\x9B\x91 STOP COMMAND RECEIVED!\n", node_id); // 🛑
    stop_relay();
  } else {
    Serial.printf("[%s] \xE2\x9D\x93 Unknown action: %s\n", node_id, action.c_str()); // ❓
    publish_response(action.c_str(), false, "Unknown action");
  }
}

void reconnect() {
  while (!client.connected()) {
    if (client.connect(node_id)) {
      String topic = String("wc/") + node_id + "/command";
      client.subscribe(topic.c_str());
      Serial.printf("[%s] MQTT connected and subscribed to %s\n", node_id, topic.c_str());
      publish_status();
    } else {
      Serial.printf("[%s] MQTT connection failed, retrying in 2 seconds...\n", node_id);
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.println("Starting main.cpp...");
  Serial.printf("[%s] Starting %s (%s) node...\n", node_id, room_name, node_type);
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);
  digitalWrite(LED_PIN, HIGH);
  Serial.printf("[%s] Testing LED...\n", node_id);
  for (int i = 0; i < 3; i++) {
    digitalWrite(LED_PIN, LOW); delay(300);
    digitalWrite(LED_PIN, HIGH); delay(300);
  }
  Serial.printf("[%s] LED test complete\n", node_id);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  publish_status();
  Serial.printf("[%s] \xF0\x9F\x8E\x89 %s ESP8266 Node is ready!\n", node_id, room_name); // 🎉
  Serial.printf("[%s] \xF0\x9F\x92\xA1 LED will blink for 4 seconds when flush command is received\n", node_id); // 💡
  Serial.printf("[%s] \xF0\x9F\x93\xA1 Status will be published every 10 seconds\n", node_id); // 📡
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();
  unsigned long now = millis();
  // Auto-off relay after 5s
  if (relayActive && now > relayOffTime) {
    stop_relay();
  }
  // Periodic publish status every 10s
  static int statusCount = 0;
  if (now - lastStatusTime > 10000) {
    statusCount++;
    Serial.printf("[%s] \xF0\x9F\x93\x8A Publishing status update #%d\n", node_id, statusCount); // 📊
    publish_status();
    lastStatusTime = now;
  }
  // Debug info every 5s
  static unsigned long lastDebug = 0;
  if (now - lastDebug > 5000) {
    const char* wifi_status = (WiFi.status() == WL_CONNECTED) ? "connected" : "disconnected";
    const char* mqtt_status = client.connected() ? "connected" : "disconnected";
    Serial.printf("[%s] \xF0\x9F\x94\x84 Status: WiFi=%s, MQTT=%s, Relay=%d\n", node_id, wifi_status, mqtt_status, digitalRead(RELAY_PIN)); // 🔄
    lastDebug = now;
  }
}
