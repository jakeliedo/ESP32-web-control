#include <ESP8266WiFi.h>
#include <PubSubClient.h>

#define RELAY_PIN D1
#define LED_PIN   LED_BUILTIN

const char* ssid = "YOUR_WIFI";
const char* password = "YOUR_PASS";
const char* mqtt_server = "192.168.1.181";
const char* node_id = "wc2";

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  delay(10);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { delay(500); }
}

void callback(char* topic, byte* payload, unsigned int length) {
  String msg;
  for (unsigned int i = 0; i < length; i++) msg += (char)payload[i];
  if (msg == "flush" || msg == "on") {
    digitalWrite(RELAY_PIN, HIGH);
    digitalWrite(LED_PIN, LOW);
    delay(4000);
    digitalWrite(RELAY_PIN, LOW);
    digitalWrite(LED_PIN, HIGH);
  }
}

void reconnect() {
  while (!client.connected()) {
    if (client.connect(node_id)) {
      client.subscribe("wc/wc2/command");
    } else {
      delay(2000);
    }
  }
}

void setup() {
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);
  digitalWrite(LED_PIN, HIGH);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();
}
