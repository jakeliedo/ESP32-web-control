#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

#define RELAY_PIN D1
#define LED_PIN   LED_BUILTIN

const char* ssid = "Michelle";
const char* password = "0908800130";
const char* mqtt_server = "192.168.1.181";
const char* node_id = "wc1";
const char* node_type = "male";
const char* room_name = "Room 1";

WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastStatusTime = 0;
unsigned long relayOffTime = 0;
bool relayActive = false;

void setup_wifi() {
  delay(10);
  for (int retry = 0; retry < 20; retry++) {
    Serial.printf("[%s] Connecting to WiFi... (%d/20)\n", node_id, retry + 1);
    if (WiFi.status() == WL_CONNECTED) break;
    WiFi.begin(ssid, password);
    delay(500);
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
  Serial.printf("[%s] Response published: %s\n", node_id, action);
}

void blink_led_4s() {
  Serial.printf("[%s] Blinking LED for 4 seconds...\n", node_id);
  for (int i = 0; i < 20; i++) {
    digitalWrite(LED_PIN, LOW);
    delay(100);
    digitalWrite(LED_PIN, HIGH);
    delay(100);
  }
  digitalWrite(LED_PIN, HIGH);
  Serial.printf("[%s] LED blinking done\n", node_id);
}

void stop_relay() {
  digitalWrite(RELAY_PIN, LOW);
  relayActive = false;
  digitalWrite(LED_PIN, HIGH);
  publish_response("stop", true, "Relay deactivated");
  Serial.printf("[%s] Relay stopped\n", node_id);
}

void execute_flush() {
  digitalWrite(RELAY_PIN, HIGH);
  relayActive = true;
  digitalWrite(LED_PIN, LOW);
  relayOffTime = millis() + 5000;
  publish_response("flush", true, "Flush executed, LED blinking 4s");
  Serial.printf("[%s] FLUSH command received!\n", node_id);
  blink_led_4s();
}

void callback(char* topic, byte* payload, unsigned int length) {
  String msg;
  for (unsigned int i = 0; i < length; i++) msg += (char)payload[i];
  String action = msg;
  Serial.print("[wc1] MQTT message received: ");
  Serial.println(msg);
  // Thử parse JSON
  StaticJsonDocument<128> doc;
  DeserializationError err = deserializeJson(doc, msg);
  if (!err) {
    if (doc.containsKey("action")) action = doc["action"].as<String>();
    Serial.print("[wc1] Parsed action: ");
    Serial.println(action);
  }
  action.trim();
  if (action == "flush" || action == "on" || action == "activate") {
    execute_flush();
  } else if (action == "status" || action == "ping") {
    publish_status();
    Serial.println("[wc1] STATUS command received!");
  } else if (action == "off" || action == "stop") {
    stop_relay();
    Serial.println("[wc1] STOP command received!");
  } else {
    publish_response(action.c_str(), false, "Unknown action");
    Serial.print("[wc1] Unknown action: ");
    Serial.println(action);
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.printf("[%s] Attempting MQTT connection...\n", node_id);
    if (client.connect(node_id)) {
      String topic = String("wc/") + node_id + "/command";
      client.subscribe(topic.c_str());
      Serial.printf("[%s] MQTT connected and subscribed to %s\n", node_id, topic.c_str());
    } else {
      Serial.printf("[%s] MQTT connection failed, retrying...\n", node_id);
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  delay(100);
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
  if (WiFi.status() == WL_CONNECTED) {
    reconnect();
    publish_status();
    Serial.printf("[%s] 🎉 %s ESP32 Node is ready!\n", node_id, room_name);
    Serial.printf("[%s] 💡 LED will blink for 4 seconds when flush command is received\n", node_id);
    Serial.printf("[%s] 📡 Status will be published every 10 seconds\n", node_id);
  } else {
    Serial.printf("[%s] Node is OFFLINE (WiFi not connected)\n", node_id);
  }
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();
  unsigned long now = millis();
  // Auto-off relay after 5s
  if (relayActive && now > relayOffTime) {
    stop_relay();
  }
  // Publish status every 10s
  if (now - lastStatusTime > 10000) {
    static int status_count = 1;
    Serial.printf("[%s] 📊 Publishing status update #%d\n", node_id, status_count++);
    publish_status();
    lastStatusTime = now;
  }
  // Print debug info every 5s
  static unsigned long lastDebug = 0;
  if (now - lastDebug > 5000) {
    const char* wifi_status = (WiFi.status() == WL_CONNECTED) ? "connected" : "disconnected";
    const char* mqtt_status = client.connected() ? "connected" : "disconnected";
    Serial.printf("[%s] 🔄 Status: WiFi=%s, MQTT=%s, Relay=%d\n", node_id, wifi_status, mqtt_status, relayActive ? 1 : 0);
    lastDebug = now;
  }
}
