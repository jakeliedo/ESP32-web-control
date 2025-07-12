#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// === Node Configuration ===
constexpr const char* NODE_ID = "wc_female_02";
constexpr const char* NODE_TYPE = "female";
constexpr const char* ROOM_NAME = "Room 2";
constexpr const char* MQTT_BROKER = "192.168.20.109";
constexpr int   MQTT_PORT = 1883;

// === GPIO Setup (adjust pins as needed for your ESP32-C3 board) ===
constexpr int STATUS_LED_PIN = 2;
constexpr int RELAY_PIN      = 5;
constexpr int INDICATOR_PIN  = 8;

constexpr int WIFI_RETRY_MAX = 40;
constexpr int WIFI_RETRY_DELAY = 250;
constexpr int WIFI_SSID_COUNT = 2;
constexpr int STATUS_PUBLISH_INTERVAL = 10000;
constexpr int RELAY_ON_TIME = 5000;

WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastStatusTime = 0;
unsigned long relayOffTime = 0;
bool relayActive = false;

void setup_pins() {
  pinMode(STATUS_LED_PIN, OUTPUT);
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(INDICATOR_PIN, OUTPUT);
  digitalWrite(STATUS_LED_PIN, HIGH);
  digitalWrite(RELAY_PIN, LOW);
  digitalWrite(INDICATOR_PIN, LOW);
}

void blink_led(unsigned int ms) {
  int cycles = ms / 200;
  for (int i = 0; i < cycles; i++) {
    digitalWrite(STATUS_LED_PIN, LOW);
    delay(100);
    digitalWrite(STATUS_LED_PIN, HIGH);
    delay(100);
  }
  digitalWrite(STATUS_LED_PIN, HIGH);
}

void setup_wifi() {
  delay(10);
  Serial.println("[room4] Starting WiFi connection...");
  WiFi.mode(WIFI_STA);
  WiFi.disconnect(true);
  delay(100);
  pinMode(STATUS_LED_PIN, OUTPUT);
  pinMode(INDICATOR_PIN, OUTPUT);
  digitalWrite(STATUS_LED_PIN, HIGH);
  digitalWrite(INDICATOR_PIN, HIGH); // Indicator LED ON while searching

  const char* ssids[WIFI_SSID_COUNT] = {"Floor 9", "WC"};
  const char* passwords[WIFI_SSID_COUNT] = {"Veg@s123", "abcd123456"};
  bool connected = false;
  while (!connected) {
    for (int net = 0; net < WIFI_SSID_COUNT && !connected; net++) {
      Serial.printf("[room4] Trying SSID: %s\n", ssids[net]);
      WiFi.begin(ssids[net], passwords[net]);
      int retry = 0;
      while (WiFi.status() != WL_CONNECTED && retry < WIFI_RETRY_MAX) {
        delay(WIFI_RETRY_DELAY);
        digitalWrite(STATUS_LED_PIN, !digitalRead(STATUS_LED_PIN));
        digitalWrite(INDICATOR_PIN, !digitalRead(INDICATOR_PIN));
        Serial.print(".");
        retry++;
      }
      if (WiFi.status() == WL_CONNECTED) {
        connected = true;
        break;
      }
      Serial.printf("\n[room4] Failed to connect to %s\n", ssids[net]);
    }
    if (!connected) {
      Serial.println("[room4] No WiFi found, resetting device in 2 seconds...");
      delay(2000);
      ESP.restart();
    }
  }
  digitalWrite(STATUS_LED_PIN, HIGH);
  digitalWrite(INDICATOR_PIN, HIGH);
  Serial.println("\n[room4] WiFi connected!");
  Serial.print("[room4] IP: ");
  Serial.println(WiFi.localIP());
  digitalWrite(INDICATOR_PIN, LOW); // Indicator LED OFF when connected
}

void publish_status(const char* custom_status = nullptr) {
  JsonDocument doc;
  doc["node_id"] = NODE_ID;
  doc["node_type"] = NODE_TYPE;
  doc["room_name"] = ROOM_NAME;
  doc["status"] = custom_status ? custom_status : (WiFi.status() == WL_CONNECTED ? "online" : "offline");
  doc["wifi_connected"] = (WiFi.status() == WL_CONNECTED);
  doc["relay_active"] = relayActive;
  doc["timestamp"] = millis() / 1000;
  char buf[256];
  size_t n = serializeJson(doc, buf);
  String topic = String("wc/") + NODE_ID + "/status";
  client.publish(topic.c_str(), buf, n);
  Serial.printf("[room4] Status published: %s\n", doc["status"].as<const char*>());
}

void publish_response(const char* action, bool success, const char* message) {
  JsonDocument doc;
  doc["node_id"] = NODE_ID;
  doc["action"] = action;
  doc["success"] = success;
  doc["message"] = message;
  doc["timestamp"] = millis() / 1000;
  char buf[256];
  size_t n = serializeJson(doc, buf);
  String topic = String("wc/") + NODE_ID + "/response";
  client.publish(topic.c_str(), buf, n);
  Serial.printf("[room4] Response published: %s (%s)\n", action, success ? "OK" : "FAIL");
}

void stop_relay() {
  digitalWrite(RELAY_PIN, LOW);
  digitalWrite(INDICATOR_PIN, LOW);
  relayActive = false;
  publish_response("stop", true, "Relay deactivated");
  publish_status("idle");
  Serial.println("[room4] Relay stopped, indicator OFF");
}

void execute_flush() {
  digitalWrite(RELAY_PIN, HIGH);
  digitalWrite(INDICATOR_PIN, HIGH);
  relayActive = true;
  relayOffTime = millis() + RELAY_ON_TIME;
  publish_response("flush", true, "Flush executed successfully");
  publish_status("flushing");
  Serial.println("[room4] FLUSH command received! Relay ON, indicator ON, blinking status LED");
  blink_led(RELAY_ON_TIME);
}

void callback(char* topic, byte* payload, unsigned int length) {
  String msg;
  for (unsigned int i = 0; i < length; i++) msg += (char)payload[i];
  String action = msg;
  Serial.print("[room4] MQTT message received: ");
  Serial.println(msg);
  JsonDocument doc;
  DeserializationError err = deserializeJson(doc, msg);
  if (!err) {
    if (doc["action"].is<String>()) action = doc["action"].as<String>();
    Serial.print("[room4] Parsed action: ");
    Serial.println(action);
  }
  action.trim();
  if (action == "flush" || action == "on" || action == "activate") {
    execute_flush();
  } else if (action == "status" || action == "ping") {
    publish_status();
    Serial.println("[room4] STATUS command received!");
  } else if (action == "off" || action == "stop") {
    stop_relay();
    Serial.println("[room4] STOP command received!");
  } else {
    publish_response(action.c_str(), false, "Unknown action");
    Serial.print("[room4] Unknown action: ");
    Serial.println(action);
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.println("[room4] Attempting MQTT connection...");
    if (client.connect(NODE_ID)) {
      String topic = String("wc/") + NODE_ID + "/command";
      client.subscribe(topic.c_str());
      Serial.print("[room4] Subscribed to topic: ");
      Serial.println(topic);
    } else {
      Serial.println("[room4] MQTT connection failed, retrying...");
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  delay(100);
  Serial.println("[room4] Starting node...");
  setup_pins();
  setup_wifi();
  client.setServer(MQTT_BROKER, MQTT_PORT);
  client.setCallback(callback);
  // Test LED startup
  blink_led(900);
  publish_status("booted");
  Serial.println("[room4] Node ready!");
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();
  unsigned long now = millis();
  if (relayActive && now > relayOffTime) {
    stop_relay();
  }
  if (now - lastStatusTime > STATUS_PUBLISH_INTERVAL) {
    publish_status();
    lastStatusTime = now;
  }
}
