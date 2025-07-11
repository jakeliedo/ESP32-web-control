#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <Arduino.h>

#define RELAY_PIN D1
#define LED_PIN   LED_BUILTIN

// WiFi networks in priority order
struct WifiNetwork {
  const char* ssid;
  const char* password;
};
WifiNetwork wifiNetworks[] = {
  {"Floor 9", "Veg@s123"}, // Corrected case
  {"Vinternal", "abcd123456"},
  {"Michelle", "0908800130"},
  {"Vtech","Veg@s123"}
};
const int wifiNetworkCount = sizeof(wifiNetworks) / sizeof(wifiNetworks[0]);

const char* mqtt_server = "192.168.1.181";
const char* node_id = "wc2";
const char* node_type = "male";
const char* room_name = "Room 2";

WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastStatusTime = 0;
unsigned long relayOffTime = 0;
bool relayActive = false;
unsigned long lastReconnectAttempt = 0;
const unsigned long reconnectInterval = 5000; // 5 seconds

// --- WiFi State Machine ---
enum WifiState { WIFI_IDLE, WIFI_SCANNING, WIFI_CONNECTING, WIFI_CONNECTED, WIFI_FAILED };
WifiState wifiState = WIFI_IDLE;
int wifiScanIndex = 0;
int wifiConnectIndex = -1;
unsigned long wifiLastAction = 0;
int wifiRetry = 0;

// --- LED Indication: Simple State Machine ---
enum LedMode {
  LED_OFF,        // Tắt
  LED_ON,         // Sáng liên tục
  LED_BLINK_SLOW, // Nháy chậm (WiFi scan/fail)
  LED_BLINK_FAST, // Nháy nhanh (WiFi/MQTT connecting)
  LED_FLASH,      // Nháy ngắn 2 lần (WiFi/MQTT connected)
  LED_FLUSH       // Nháy 4s khi flush
};
LedMode ledMode = LED_OFF;
unsigned long ledTick = 0;
int ledCount = 0;

void setLed(LedMode mode) {
  ledMode = mode;
  ledTick = millis();
  ledCount = 0;
}

void handleLed() {
  unsigned long now = millis();
  switch (ledMode) {
    case LED_OFF:
      digitalWrite(LED_PIN, HIGH);
      break;
    case LED_ON:
      digitalWrite(LED_PIN, LOW);
      break;
    case LED_BLINK_SLOW:
      if (now - ledTick > 400) {
        digitalWrite(LED_PIN, !digitalRead(LED_PIN));
        ledTick = now;
      }
      break;
    case LED_BLINK_FAST:
      if (now - ledTick > 120) {
        digitalWrite(LED_PIN, !digitalRead(LED_PIN));
        ledTick = now;
      }
      break;
    case LED_FLASH:
      if (ledCount < 4) {
        if (now - ledTick > 80) {
          digitalWrite(LED_PIN, ledCount % 2 == 0 ? LOW : HIGH);
          ledTick = now;
          ledCount++;
        }
      } else {
        digitalWrite(LED_PIN, HIGH);
        ledMode = LED_OFF;
      }
      break;
    case LED_FLUSH:
      if (ledCount < 20) {
        if (now - ledTick > 100) {
          digitalWrite(LED_PIN, ledCount % 2 == 0 ? LOW : HIGH);
          ledTick = now;
          ledCount++;
        }
      } else {
        digitalWrite(LED_PIN, HIGH);
        ledMode = LED_OFF;
      }
      break;
  }
}

void start_wifi_scan() {
  wifiState = WIFI_SCANNING;
  wifiScanIndex = 0;
  wifiConnectIndex = -1;
  wifiLastAction = millis();
  Serial.println("[wc2] Scanning for WiFi networks...");
  WiFi.disconnect();
  WiFi.scanDelete();
  WiFi.scanNetworks(true); // async scan
  setLed(LED_BLINK_SLOW);
}

void handle_wifi() {
  unsigned long now = millis();
  if (wifiState == WIFI_SCANNING) {
    int8_t n = WiFi.scanComplete();
    if (n == WIFI_SCAN_RUNNING) return;
    if (n < 0) {
      if (now - wifiLastAction > 5000) {
        Serial.println("[wc2] WiFi scan failed, retrying...");
        WiFi.scanNetworks(true);
        wifiLastAction = now;
      }
      setLed(LED_BLINK_SLOW);
      return;
    }
    Serial.print("[wc2] Found "); Serial.print(n); Serial.println(" WiFi networks.");
    for (int i = 0; i < wifiNetworkCount; i++) {
      for (int j = 0; j < n; j++) {
        if (String(WiFi.SSID(j)).equalsIgnoreCase(String(wifiNetworks[i].ssid))) {
          wifiConnectIndex = i;
          break;
        }
      }
      if (wifiConnectIndex != -1) break;
    }
    WiFi.scanDelete();
    if (wifiConnectIndex == -1) {
      Serial.println("[wc2] No known WiFi networks found!");
      wifiState = WIFI_FAILED;
      setLed(LED_BLINK_SLOW);
      return;
    }
    Serial.print("[wc2] Connecting to WiFi: ");
    Serial.println(wifiNetworks[wifiConnectIndex].ssid);
    WiFi.begin(wifiNetworks[wifiConnectIndex].ssid, wifiNetworks[wifiConnectIndex].password);
    wifiRetry = 0;
    wifiLastAction = now;
    wifiState = WIFI_CONNECTING;
    setLed(LED_BLINK_FAST);
  } else if (wifiState == WIFI_CONNECTING) {
    if (WiFi.status() == WL_CONNECTED) {
      Serial.print("[wc2] WiFi connected! IP: ");
      Serial.println(WiFi.localIP());
      wifiState = WIFI_CONNECTED;
      setLed(LED_FLASH);
      return;
    }
    if (now - wifiLastAction > 5000) {
      wifiRetry++;
      if (wifiRetry > 5) {
        Serial.println("[wc2] WiFi connection failed after 5 attempts!");
        wifiState = WIFI_FAILED;
        setLed(LED_BLINK_SLOW);
        return;
      }
      Serial.print("[wc2] WiFi retry "); Serial.println(wifiRetry);
      WiFi.disconnect();
      WiFi.begin(wifiNetworks[wifiConnectIndex].ssid, wifiNetworks[wifiConnectIndex].password);
      wifiLastAction = now;
      setLed(LED_BLINK_FAST);
    }
  }
}

// --- Non-blocking LED Blink ---
enum LedEffect { LED_NONE, LED_BLINK_4S };
LedEffect ledEffect = LED_NONE;
unsigned long ledEffectStart = 0;
int ledEffectStep = 0;
void startLedEffect(LedEffect effect) {
  ledEffect = effect;
  ledEffectStart = millis();
  ledEffectStep = 0;
}
void handleLedEffect() {
  if (ledEffect == LED_BLINK_4S) {
    unsigned long now = millis();
    if (ledEffectStep < 20) {
      if ((now - ledEffectStart) >= 100) {
        digitalWrite(LED_PIN, ledEffectStep % 2 == 0 ? LOW : HIGH);
        ledEffectStart = now;
        ledEffectStep++;
      }
    } else {
      digitalWrite(LED_PIN, HIGH);
      ledEffect = LED_NONE;
      Serial.println("[wc2] LED blinking done");
    }
  }
}

bool setup_wifi() {
  delay(10);
  Serial.println("[wc2] Scanning for WiFi networks...");
  int8_t n = WiFi.scanNetworks();
  Serial.print("[wc2] Found ");
  Serial.print(n);
  Serial.println(" WiFi networks.");
  int chosen = -1;
  for (int i = 0; i < wifiNetworkCount; i++) {
    Serial.print("[wc2] Checking known SSID: ");
    Serial.println(wifiNetworks[i].ssid);
    for (int j = 0; j < n; j++) {
      Serial.print("[wc2]  - Found SSID: ");
      Serial.println(WiFi.SSID(j));
      if (String(WiFi.SSID(j)).equalsIgnoreCase(String(wifiNetworks[i].ssid))) {
        chosen = i;
        Serial.print("[wc2]  -> Match found: ");
        Serial.println(wifiNetworks[i].ssid);
        break;
      }
    }
    if (chosen != -1) break;
  }
  if (chosen == -1) {
    Serial.println("[wc2] No known WiFi networks found!");
    return false;
  }
  Serial.print("[wc2] Connecting to WiFi: ");
  Serial.println(wifiNetworks[chosen].ssid);
  WiFi.begin(wifiNetworks[chosen].ssid, wifiNetworks[chosen].password);
  int retry = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    retry++;
    if (retry % 10 == 0) {
      Serial.print(" [wc2] Still connecting (attempt ");
      Serial.print(retry);
      Serial.println(")");
    }
    if (retry > 10) {
      Serial.println("\n[wc2] WiFi connection failed after 10 attempts! Resetting device...");
      ESP.restart();
      delay(1000); // Give time for restart
      return false;
    }
  }
  Serial.println("\n[wc2] WiFi connected!");
  Serial.print("[wc2] IP: ");
  Serial.println(WiFi.localIP());
  return true;
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
  Serial.println("[wc2] Status published");
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
  setLed(LED_OFF);
  publish_response("stop", true, "Relay deactivated");
  Serial.println("[wc2] Relay stopped");
}

void execute_flush() {
  digitalWrite(RELAY_PIN, HIGH);
  relayActive = true;
  setLed(LED_FLUSH);
  relayOffTime = millis() + 5000;
  publish_response("flush", true, "Flush executed, LED blinking 4s");
  Serial.println("[wc2] FLUSH command received!");
}

void callback(char* topic, byte* payload, unsigned int length) {
  String msg;
  for (unsigned int i = 0; i < length; i++) msg += (char)payload[i];
  String action = msg;
  Serial.print("[wc2] MQTT message received: ");
  Serial.println(msg);
  // Thử parse JSON
  StaticJsonDocument<128> doc;
  DeserializationError err = deserializeJson(doc, msg);
  if (!err) {
    if (doc.containsKey("action")) action = doc["action"].as<String>();
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
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[wc2] WiFi not connected, cannot connect to MQTT!");
    setLed(LED_BLINK_SLOW);
    return;
  }
  Serial.println("[wc2] Attempting MQTT connection...");
  setLed(LED_BLINK_FAST);
  if (client.connect(node_id)) {
    String topic = String("wc/") + node_id + "/command";
    client.subscribe(topic.c_str());
    Serial.print("[wc2] Subscribed to topic: ");
    Serial.println(topic);
    setLed(LED_FLASH);
  } else {
    Serial.print("[wc2] MQTT connection failed, rc=");
    Serial.print(client.state());
    Serial.println(". Will retry in 5 seconds...");
    setLed(LED_BLINK_FAST);
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
  start_wifi_scan();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  Serial.println("[wc2] Node ready!");
}

void loop() {
  handle_wifi();
  handleLed();
  if (relayActive) setLed(LED_ON);
  if (wifiState != WIFI_CONNECTED) return;
  if (!client.connected()) {
    unsigned long now = millis();
    if (now - lastReconnectAttempt > reconnectInterval) {
      Serial.println("[wc2] MQTT not connected, calling reconnect()...");
      reconnect();
      lastReconnectAttempt = now;
    }
  } else {
    client.loop();
  }
  unsigned long now = millis();
  if (relayActive && now > relayOffTime) {
    stop_relay();
  }
  if (now - lastStatusTime > 10000) {
    Serial.println("[wc2] Publishing periodic status update...");
    publish_status();
    lastStatusTime = now;
  }
}
