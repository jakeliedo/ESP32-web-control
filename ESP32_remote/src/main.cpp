#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <HardwareSerial.h>
#include "DMT_Display.h"

// === Node Configuration ===
#define NODE_ID "esp32_remote"
#define DEVICE_NAME "ESP32 Remote Control"

// === MQTT Configuration (same as room4) ===
#define MQTT_BROKER "192.168.1.183"
#define MQTT_PORT 1883

// === WiFi Credentials (same as room4) ===
const char* ssid1 = "Floor 9";
const char* pass1 = "Veg@s123";
const char* ssid2 = "Vinternal";
const char* pass2 = "abcd1234";
const char* ssid3 = "Roll";
const char* pass3 = "0908800130";

// === DMT Configuration ===
#define DMT_TX_PIN 21
#define DMT_RX_PIN 20

// === GPIO Setup ===
const int STATUS_LED_PIN = 8; // Built-in LED for ESP32-C3

// === Node List for Control ===
const char* nodeList[] = {"wc_male_01", "wc_male_02", "wc_female_01", "wc_female_02"};
const char* nodeNames[] = {"Male WC 1", "Male WC 2", "Female WC 1", "Female WC 2"};
const uint16_t touchVPAddresses[] = {0x2100, 0x2200, 0x2300, 0x2400};
const uint16_t statusVPAddresses[] = {0x3100, 0x3200, 0x3300, 0x3400};
const int numNodes = 4;

// === Global Objects ===
WiFiClient espClient;
PubSubClient mqttClient(espClient);
HardwareSerial DMTSerial(1);
DMT_Display dmtDisplay(&DMTSerial);

// === Global Variables ===
unsigned long lastStatusTime = 0;
unsigned long lastHeartbeat = 0;
bool nodeStatus[numNodes] = {false}; // Track node online status
unsigned long lastNodeResponse[numNodes] = {0}; // Track last response time
int currentPage = 0; // 0 = main control, 1 = wifi debug

// Button reset mechanism (global)
unsigned long resetTime[numNodes] = {0};
bool resetPending[numNodes] = {false};

// WiFi non-blocking connection state
enum WiFiState {
  WIFI_IDLE,
  WIFI_SCANNING,
  WIFI_CONNECTING,
  WIFI_CONNECTED,
  WIFI_FAILED
};
WiFiState wifiState = WIFI_IDLE;
unsigned long lastWifiActionTime = 0;
int wifiConnectTries = 0;

// === Function Declarations ===
void setupGPIO();
void manageWiFi(); // Replaces connectWiFi() in loop
void startWiFiConnection(); // Starts the connection process
void connectMQTT();
void mqttCallback(char* topic, byte* payload, unsigned int length);
void publishStatus();
void sendFlushCommand(int nodeIndex);
void updateNodeStatus(const char* nodeId, bool online);
void updateDMTDisplay();
void handleDMTTouch(uint16_t vpAddress, uint16_t vpData);
void handleDMTTouchWithKeyCode(uint16_t vpAddress, uint8_t keyCode, uint16_t vpData);
void showWiFiDebugPage();
void showMainPage();

void setup() {
  Serial.begin(115200);
  delay(3000); // Increased delay for serial to initialize properly
  
  // Test Serial immediately
  Serial.println("DEBUG: Serial initialization test");
  Serial.println("DEBUG: If you see this, Serial is working");
  
  Serial.println("\n=== ESP32 Remote Control Starting ===");
  Serial.printf("Chip Model: %s\n", ESP.getChipModel());
  Serial.printf("Chip Revision: %d\n", ESP.getChipRevision());
  Serial.printf("Free Heap: %d bytes\n", ESP.getFreeHeap());
  Serial.printf("Flash Size: %d bytes\n", ESP.getFlashChipSize());
  
  Serial.println("DEBUG: About to call setupGPIO()");
  setupGPIO();
  
  Serial.println("DEBUG: About to initialize DMT Display");
  dmtDisplay.begin(115200, DMT_RX_PIN, DMT_TX_PIN);
  dmtDisplay.setVPDataCallback(handleDMTTouch);
  dmtDisplay.setVPDataWithKeyCodeCallback(handleDMTTouchWithKeyCode);
  
  Serial.println("✓ DMT Display initialized");
  Serial.println("DEBUG: About to write Booting text to DMT");
  
  dmtDisplay.writeText(0x5000, "Booting...");
  delay(1000);
  
  Serial.println("DEBUG: Starting WiFi connection process...");
  startWiFiConnection(); // Start the non-blocking connection
  
  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setCallback(mqttCallback);
  // connectMQTT() will be called from manageWiFi() after connection
  
  showMainPage();
  
  Serial.println("=== ESP32 Remote Control Ready ===\n");
}

void loop() {
  manageWiFi(); // Handle WiFi state machine
  
  // Handle MQTT reconnection only if WiFi is connected
  if (WiFi.status() == WL_CONNECTED && !mqttClient.connected()) {
    connectMQTT();
  }
  
  if (mqttClient.connected()) {
    mqttClient.loop();
  }
  
  dmtDisplay.handleIncomingData();
  
  // Blink status LED
  static unsigned long lastBlink = 0;
  if (millis() - lastBlink > 1000) {
    digitalWrite(STATUS_LED_PIN, !digitalRead(STATUS_LED_PIN));
    lastBlink = millis();
  }
  
  // Publish status every 30 seconds
  if (millis() - lastStatusTime > 30000) {
    publishStatus();
    lastStatusTime = millis();
  }
  
  // Update display every 5 seconds
  static unsigned long lastDisplayUpdate = 0;
  if (millis() - lastDisplayUpdate > 5000) {
    updateDMTDisplay();
    lastDisplayUpdate = millis();
  }
  
  // System heartbeat every 60 seconds
  if (millis() - lastHeartbeat > 60000) {
    Serial.printf("💓 Uptime: %lu seconds, Heap: %d bytes, WiFi Status: %d, MQTT: %s\n", 
                  millis() / 1000, ESP.getFreeHeap(), WiFi.status(), mqttClient.connected() ? "OK" : "FAIL");
    lastHeartbeat = millis();
  }
  
  // Handle button reset (non-blocking)
  for (int i = 0; i < numNodes; i++) {
    if (resetPending[i] && millis() >= resetTime[i]) {
      Serial.printf("🔄 Resetting Button %d: VP=0x%04X to 0x0000\n", i+1, touchVPAddresses[i]);
      dmtDisplay.writeVP(touchVPAddresses[i], (uint16_t)0x0000);
      resetPending[i] = false;
    }
  }
}

void setupGPIO() {
  pinMode(STATUS_LED_PIN, OUTPUT);
  digitalWrite(STATUS_LED_PIN, LOW);
  Serial.println("✓ GPIO initialized");
}

void startWiFiConnection() {
  Serial.println("🔍 Starting WiFi Scan...");
  dmtDisplay.writeText(0x5100, "Scanning WiFi...");
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  wifiState = WIFI_SCANNING;
  lastWifiActionTime = millis();
}

void manageWiFi() {
  unsigned long currentTime = millis();

  switch (wifiState) {
    case WIFI_IDLE:
      // Do nothing, wait for something to trigger a connection
      break;

    case WIFI_SCANNING:
      if (currentTime - lastWifiActionTime > 100) { // Wait 100ms for disconnect to settle
        int n = WiFi.scanNetworks();
        Serial.printf("📡 Found %d networks\n", n);

        if (n == 0) {
          Serial.println("❌ No networks found, retrying scan in 10s...");
          dmtDisplay.writeText(0x5100, "No WiFi found!");
          wifiState = WIFI_FAILED; // Go to failed state to handle retry
          lastWifiActionTime = currentTime;
          return;
        }

        bool found = false;
        String connectingSSID = "";

        // Priority order: Roll -> Floor 9 -> Vinternal
        for (int i = 0; i < n; ++i) {
          String ssid = WiFi.SSID(i);
          if (ssid == "Roll") {
            connectingSSID = "Roll";
            WiFi.begin(ssid3, pass3);
            found = true;
            break;
          } else if (ssid == "Floor 9") {
            connectingSSID = "Floor 9";
            WiFi.begin(ssid1, pass1);
            found = true;
            break;
          } else if (ssid == "Vinternal") {
            connectingSSID = "Vinternal";
            WiFi.begin(ssid2, pass2);
            found = true;
            break;
          }
        }

        if (!found) {
          Serial.println("❌ No known WiFi networks found, retrying scan in 10s...");
          dmtDisplay.writeText(0x5100, "No WiFi found!");
          wifiState = WIFI_FAILED; // Go to failed state to handle retry
          lastWifiActionTime = currentTime;
        } else {
          Serial.printf("🔄 Connecting to %s...\n", connectingSSID.c_str());
          dmtDisplay.writeText(0x5100, ("Connecting " + connectingSSID + "...").c_str());
          wifiState = WIFI_CONNECTING;
          wifiConnectTries = 0;
          lastWifiActionTime = currentTime;
        }
      }
      break;

    case WIFI_CONNECTING:
      // Blinking icon effect
      if (currentTime - lastWifiActionTime >= 500) {
        bool iconState = (wifiConnectTries % 2 == 0);
        dmtDisplay.writeVP(0x3500, iconState ? (uint16_t)0x0001 : (uint16_t)0x0000);
        lastWifiActionTime = currentTime;
        wifiConnectTries++;
      }

      if (WiFi.status() == WL_CONNECTED) {
        Serial.printf("\n✅ WiFi Connected: %s\n", WiFi.SSID().c_str());
        Serial.printf("📶 IP: %s, RSSI: %d dBm\n", WiFi.localIP().toString().c_str(), WiFi.RSSI());
        
        dmtDisplay.writeVP(0x3500, (uint16_t)0x0001); // Solid ON
        String wifiInfo = "WiFi: " + WiFi.SSID() + " (" + String(WiFi.RSSI()) + "dBm)";
        dmtDisplay.writeText(0x5100, wifiInfo.c_str());
        
        wifiState = WIFI_CONNECTED;
        connectMQTT(); // Connect to MQTT now that WiFi is up
      } else if (wifiConnectTries > 40) { // Timeout after 20 seconds
        Serial.println("\n❌ WiFi connection failed (timeout)");
        dmtDisplay.writeText(0x5100, "WiFi Failed!");
        dmtDisplay.writeVP(0x3500, (uint16_t)0x0000); // Solid OFF
        wifiState = WIFI_FAILED;
        lastWifiActionTime = currentTime;
      }
      break;

    case WIFI_CONNECTED:
      if (WiFi.status() != WL_CONNECTED) {
        Serial.println("⚠️ WiFi disconnected!");
        dmtDisplay.writeVP(0x3500, (uint16_t)0x0000); // Icon OFF
        dmtDisplay.writeText(0x5100, "WiFi Disconnected!");
        mqttClient.disconnect();
        wifiState = WIFI_IDLE; // Reset state machine
        startWiFiConnection(); // Re-start the connection process
      }
      break;

    case WIFI_FAILED:
      // Wait for 10 seconds before trying to connect again
      if (currentTime - lastWifiActionTime > 10000) {
        Serial.println("🔄 Retrying WiFi connection...");
        wifiState = WIFI_IDLE;
        startWiFiConnection();
      }
      break;
  }
}

void connectMQTT() {
  while (!mqttClient.connected()) {
    Serial.print("🔗 MQTT connecting...");
    
    if (mqttClient.connect(NODE_ID)) {
      Serial.println(" ✅ connected!");
      
      // Subscribe to all node status topics
      for (int i = 0; i < numNodes; i++) {
        String statusTopic = String("wc/") + nodeList[i] + "/status";
        String responseTopic = String("wc/") + nodeList[i] + "/response";
        
        mqttClient.subscribe(statusTopic.c_str());
        mqttClient.subscribe(responseTopic.c_str());
      }
      
      publishStatus();
      dmtDisplay.writeText(0x5200, "MQTT Connected");
      
    } else {
      Serial.printf(" ❌ failed, rc=%d\n", mqttClient.state());
      dmtDisplay.writeText(0x5200, "MQTT Failed");
      delay(5000);
    }
  }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  String msgStr;
  for (unsigned int i = 0; i < length; i++) {
    msgStr += (char)payload[i];
  }
  
  // Parse message
  StaticJsonDocument<256> doc;
  DeserializationError err = deserializeJson(doc, msgStr);
  
  if (!err && doc.containsKey("node_id")) {
    String nodeId = doc["node_id"].as<String>();
    
    // Update node status
    for (int i = 0; i < numNodes; i++) {
      if (nodeId == nodeList[i]) {
        if (doc.containsKey("status")) {
          String status = doc["status"].as<String>();
          updateNodeStatus(nodeList[i], status == "online");
        }
        lastNodeResponse[i] = millis();
        break;
      }
    }
  }
}

void publishStatus() {
  if (!mqttClient.connected()) return;
  
  StaticJsonDocument<256> doc;
  doc["node_id"] = NODE_ID;
  doc["device_name"] = DEVICE_NAME;
  doc["status"] = "online";
  doc["wifi_connected"] = (WiFi.status() == WL_CONNECTED);
  doc["timestamp"] = millis();
  doc["free_memory"] = ESP.getFreeHeap();
  doc["rssi"] = WiFi.RSSI();
  
  String topic = String("wc/") + NODE_ID + "/status";
  char buffer[256];
  size_t n = serializeJson(doc, buffer);
  
  mqttClient.publish(topic.c_str(), buffer, n);
}

void sendFlushCommand(int nodeIndex) {
  if (!mqttClient.connected() || nodeIndex < 0 || nodeIndex >= numNodes) return;
  
  StaticJsonDocument<128> doc;
  doc["action"] = "flush";
  doc["timestamp"] = millis();
  
  String topic = String("wc/") + nodeList[nodeIndex] + "/command";
  char buffer[128];
  size_t n = serializeJson(doc, buffer);
  
  mqttClient.publish(topic.c_str(), buffer, n);
  
  // Update display
  String message = "FLUSH -> " + String(nodeNames[nodeIndex]);
  dmtDisplay.writeText(0x5300, message.c_str());
  
  // Reset flush button image to 0x0000 after delay (non-blocking)
  // Schedule reset for 1 second later
  Serial.printf("📅 Scheduling Button %d Reset: VP=0x%04X in 1000ms\n", nodeIndex+1, touchVPAddresses[nodeIndex]);
  resetTime[nodeIndex] = millis() + 1000;
  resetPending[nodeIndex] = true;
}

void updateNodeStatus(const char* nodeId, bool online) {
  for (int i = 0; i < numNodes; i++) {
    if (strcmp(nodeId, nodeList[i]) == 0) {
      nodeStatus[i] = online;
      break;
    }
  }
}

void updateDMTDisplay() {
  if (currentPage == 0) {
    // Main control page - update node status and icon
    Serial.println("🔄 Updating DMT Display - Main Page");
    const uint16_t iconVPAddresses[] = {0x4100, 0x4200, 0x4300, 0x4400};
    for (int i = 0; i < numNodes; i++) {
      String statusText = String(nodeNames[i]) + ": " + (nodeStatus[i] ? "ONLINE" : "OFFLINE");
      Serial.printf("   Node %d (%s): %s\n", i+1, nodeNames[i], nodeStatus[i] ? "ONLINE" : "OFFLINE");
      dmtDisplay.writeText(statusVPAddresses[i], statusText.c_str());
      // Update icon online/offline
      dmtDisplay.showNodeOnlineIcon(iconVPAddresses[i], nodeStatus[i]);
    }
  } else if (currentPage == 1) {
    // WiFi debug page - update connection info
    Serial.println("🔄 Updating DMT Display - WiFi Debug Page");
    showWiFiDebugPage();
  }
}

void handleDMTTouch(uint16_t vpAddress, uint16_t vpData) {
  Serial.printf("🎯 DMT Touch Handler: VP=0x%04X, Data=0x%04X\n", vpAddress, vpData);
  
  // Check for flush button press (VP2100-2400) - only respond to 0x0001 data
  for (int i = 0; i < numNodes; i++) {
    if (vpAddress == touchVPAddresses[i] && vpData == 0x0001) {
      Serial.printf("✅ FLUSH: %s (VP=0x%04X)\n", nodeNames[i], vpAddress);
      sendFlushCommand(i);
      return;
    }
  }
  
  // Check for page switching (VP1000 = main page, VP1001 = wifi debug)
  if (vpAddress == 0x1000 && vpData == 0x0001) {
    Serial.printf("📄 Page Switch: Main Page (VP=0x%04X)\n", vpAddress);
    currentPage = 0;
    showMainPage();
  } else if (vpAddress == 0x1001 && vpData == 0x0001) {
    Serial.printf("📄 Page Switch: WiFi Debug (VP=0x%04X)\n", vpAddress);
    currentPage = 1;
    showWiFiDebugPage();
  }
  
  // Test WiFi reconnection (VP=0x5000 to trigger reconnect for testing blink)
  if (vpAddress == 0x5000 && vpData == 0x0001) {
    Serial.printf("🔧 TEST: Force WiFi Reconnect (VP=0x%04X)\n", vpAddress);
    WiFi.disconnect();
    delay(1000);
    startWiFiConnection();
    return;
  }
  
  // Log unhandled touch events
  if (vpData == 0x0001) {
    Serial.printf("⚠️  Unhandled Touch: VP=0x%04X, Data=0x%04X\n", vpAddress, vpData);
  }
}

void handleDMTTouchWithKeyCode(uint16_t vpAddress, uint8_t keyCode, uint16_t vpData) {
  Serial.printf("🎯 DMT Touch Handler with KeyCode: VP=0x%04X, KeyCode=0x%02X, Data=0x%04X\n", 
                vpAddress, keyCode, vpData);
  
  // Check for flush button press (VP2100-2400) - only respond to 0x0001 data
  for (int i = 0; i < numNodes; i++) {
    if (vpAddress == touchVPAddresses[i] && vpData == 0x0001) {
      Serial.printf("✅ FLUSH with KeyCode: %s (VP=0x%04X, KeyCode=0x%02X)\n", 
                    nodeNames[i], vpAddress, keyCode);
      sendFlushCommand(i);
      return;
    }
  }
  
  // Check for page switching (VP1000 = main page, VP1001 = wifi debug)
  if (vpAddress == 0x1000 && vpData == 0x0001) {
    Serial.printf("📄 Page Switch with KeyCode: Main Page (VP=0x%04X, KeyCode=0x%02X)\n", 
                  vpAddress, keyCode);
    currentPage = 0;
    showMainPage();
    showWiFiDebugPage();
  } else if (vpAddress == 0x1001 && vpData == 0x0001) {
    Serial.printf("📄 Page Switch with KeyCode: WiFi Debug (VP=0x%04X, KeyCode=0x%02X)\n", 
                  vpAddress, keyCode);
    currentPage = 1;
    showWiFiDebugPage();
  }
  
  // Test WiFi reconnection (VP=0x5000 to trigger reconnect for testing blink)
  if (vpAddress == 0x5000 && vpData == 0x0001) {
    Serial.printf("🔧 TEST with KeyCode: Force WiFi Reconnect (VP=0x%04X, KeyCode=0x%02X)\n", 
                  vpAddress, keyCode);
    WiFi.disconnect();
    delay(1000);
    startWiFiConnection();
    return;
  }
  
  // Log unhandled touch events
  if (vpData == 0x0001) {
    Serial.printf("⚠️  Unhandled Touch with KeyCode: VP=0x%04X, KeyCode=0x%02X, Data=0x%04X\n", 
                  vpAddress, keyCode, vpData);
  }
}

void showMainPage() {
  currentPage = 0;
  dmtDisplay.writeText(0x5000, "ESP32 Remote Control");
  dmtDisplay.writeText(0x5400, "Touch nodes to FLUSH");
  
  // Initialize node status display
  for (int i = 0; i < numNodes; i++) {
    String statusText = String(nodeNames[i]) + ": CHECKING...";
    dmtDisplay.writeText(statusVPAddresses[i], statusText.c_str());
  }
}

void showWiFiDebugPage() {
  currentPage = 1;
  dmtDisplay.writeText(0x5000, "WiFi Debug Info");
  
  String ssid = "SSID: " + WiFi.SSID();
  String ip = "IP: " + WiFi.localIP().toString();
  String rssi = "RSSI: " + String(WiFi.RSSI()) + " dBm";
  String mqtt = "MQTT: " + String(mqttClient.connected() ? "Connected" : "Disconnected");
  
  dmtDisplay.writeText(0x5500, ssid.c_str());
  dmtDisplay.writeText(0x5600, ip.c_str());
  dmtDisplay.writeText(0x5700, rssi.c_str());
  dmtDisplay.writeText(0x5800, mqtt.c_str());
}
