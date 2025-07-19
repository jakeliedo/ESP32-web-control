#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

#define RELAY_PIN D1
#define LED_PIN   LED_BUILTIN

const char* ssid = "Roll";
const char* password = "0908800130";
const char* mqtt_server = "192.168.1.181";
const char* node_id = "wc1";
const char* node_type = "female";
const char* room_name = "Room 1";

WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastStatusTime = 0;
unsigned long relayOffTime = 0;
bool relayActive = false;

void setup_wifi() {
  delay(10);
  Serial.print("[wc1] Connecting to WiFi");
  WiFi.begin(ssid, password);
  int retry = 0;
  bool ledState = false;
  pinMode(LED_PIN, OUTPUT);
  unsigned long lastBlink = millis();
  unsigned long blinkInterval = 250;
  unsigned long startAttempt = millis();
  while (WiFi.status() != WL_CONNECTED) {
    unsigned long now = millis();
    if (now - lastBlink >= blinkInterval) {
      ledState = !ledState;
      digitalWrite(LED_PIN, ledState ? LOW : HIGH); // Blink LED (active LOW)
      lastBlink = now;
      Serial.print(".");
      retry++;
    }
    if (retry > 40) {
      digitalWrite(LED_PIN, HIGH); // Turn off LED if failed
      Serial.println("\n[wc1] WiFi connection failed!");
      return;
    }
    yield(); // Allow background tasks (important for ESP8266)
  }
  digitalWrite(LED_PIN, HIGH); // Turn off LED when connected
  Serial.println("\n[wc1] WiFi connected!");
  Serial.print("[wc1] IP: ");
  Serial.println(WiFi.localIP());
  int rssi = WiFi.RSSI();
  Serial.print("[wc1] WiFi RSSI after connect: ");
  Serial.println(rssi);
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
  int rssi = WiFi.RSSI();
  doc["rssi"] = rssi;
  char buf[256];
  size_t n = serializeJson(doc, buf);
  String topic = String("wc/") + node_id + "/status";
  client.publish(topic.c_str(), buf, n);
  Serial.print("[wc1] Status published, RSSI: ");
  Serial.println(rssi);
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
  Serial.print("[wc1] Response published: ");
  Serial.println(action);
}

void blink_led_4s() {
  Serial.println("[wc1] Blinking LED for 4 seconds...");
  for (int i = 0; i < 20; i++) {
    digitalWrite(LED_PIN, LOW);
    delay(100);
    digitalWrite(LED_PIN, HIGH);
    delay(100);
  }
  digitalWrite(LED_PIN, HIGH);
  Serial.println("[wc1] LED blinking done");
}

void stop_relay() {
  digitalWrite(RELAY_PIN, LOW);
  relayActive = false;
  digitalWrite(LED_PIN, HIGH);
  publish_response("stop", true, "Relay deactivated");
  Serial.println("[wc1] Relay stopped");
}

void execute_flush() {
  int relay_pins[] = {D0, D1, D2, D3, D4, D5, D6, D7, D8};
  Serial.println("[wc1] FLUSH: Turning all relay pins D0-D8 ON for 4 seconds");
  for (int i = 0; i < 9; i++) {
    pinMode(relay_pins[i], OUTPUT);
    digitalWrite(relay_pins[i], HIGH); // Use LOW if relay is active LOW
  }
  relayActive = true;
  digitalWrite(LED_PIN, LOW);
  publish_response("flush", true, "Flush executed, LED blinking 4s");
  Serial.println("[wc1] FLUSH command received!");
  blink_led_4s();
  delay(4000);
  for (int i = 0; i < 9; i++) {
    digitalWrite(relay_pins[i], LOW); // Use HIGH if relay is active LOW
  }
  relayActive = false;
  digitalWrite(LED_PIN, HIGH);
  Serial.println("[wc1] FLUSH: All relay pins OFF");
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
    Serial.println("[wc1] Attempting MQTT connection...");
    if (client.connect(node_id)) {
      String topic = String("wc/") + node_id + "/command";
      client.subscribe(topic.c_str());
      Serial.print("[wc1] Subscribed to topic: ");
      Serial.println(topic);
      // In ra RSSI sau khi kết nối broker
      int rssi = WiFi.RSSI();
      Serial.print("[wc1] WiFi RSSI after MQTT connect: ");
      Serial.println(rssi);
    } else {
      Serial.println("[wc1] MQTT connection failed, retrying...");
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  delay(100);
  Serial.println("[wc1] Starting node...");
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);
  digitalWrite(LED_PIN, HIGH);
  setup_wifi();
  Serial.println("[wc1] WiFi connected!");
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  // Test LED startup
  Serial.println("[wc1] Testing LED...");
  for (int i = 0; i < 3; i++) {
    digitalWrite(LED_PIN, LOW); delay(300);
    digitalWrite(LED_PIN, HIGH); delay(300);
  }
  Serial.println("[wc1] LED test complete");
  publish_status();
  Serial.println("[wc1] Node ready!");
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
