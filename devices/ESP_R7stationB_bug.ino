// Robin Vize 22/11/19
// Sniffer+ publish field 'bugs':
//  Wifi connection, MQTT connection and publish,
//  NTP server time usage and I/O expanders

#include <ESP8266WiFi.h>
#include <Ticker.h>
#include <AsyncMqttClient.h>
#include <WiFiUdp.h>
#include <Wire.h>
#include <TimeLib.h>
#include <NtpClientLib.h>

// Expander MCP23017 I2C info
#define MCP_ADDR_1 0b0100001 // A2,A1,A0 = 0,0,1

// WiFi credentials
#define WIFI_SSID "UPA Devices"
#define WIFI_PASSWORD "UPAD3vic3s2018!"

// MQTT server/broker credentials
#define MQTT_HOST "UMGSVRIIOT01.WORLD.BIZ"
#define MQTT_PORT 1883

// Library objects
AsyncMqttClient mqttClient;
Ticker mqttReconnectTimer;
WiFiEventHandler wifiConnectHandler;
WiFiEventHandler wifiDisconnectHandler;
Ticker wifiReconnectTimer;

// Set all internal pull-ups (100k) on expander IC
void setPullUps(int addr, uint8_t a, uint8_t b) {
  Wire.beginTransmission(addr);
  Wire.write(0x0C); // starts at GPIOA register address
  Wire.write(a); // A7:0 pull-ups
  Wire.write(b); // B7:0 pull-ups (note: sequential write) 
  Wire.endTransmission();
}

// Read all 16 GPIO pins on a single expander
uint16_t readGPIO(int addr) {
  Wire.beginTransmission(addr);
  Wire.write(0x12);
  Wire.endTransmission();
  Wire.requestFrom(addr, 2);
  uint8_t a = Wire.read(); // GPIOA
  uint8_t b = Wire.read(); // GPIOB
  uint16_t ab = (a << 8) | b;
  return ab;
}

// Connect to WiFi
void connectToWifi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
}

// Connect to MQTT server/broker (Mosquitto)
void connectToMqtt() {
  mqttClient.connect();
}

// Reconnect to MQTT server/broker (Mosquitto) if WiFi dropped
void onWifiConnect(const WiFiEventStationModeGotIP& event) {
  connectToMqtt();
}

// Detach MQTT connection is WiFi dropped
void onWifiDisconnect(const WiFiEventStationModeDisconnected& event) {
  mqttReconnectTimer.detach(); // ensure we don't reconnect to MQTT while reconnecting to Wi-Fi
  wifiReconnectTimer.once(2, connectToWifi);
}

// Reconnect to MQTT if dropped connection to server
void onMqttDisconnect(AsyncMqttClientDisconnectReason reason) {
  if (WiFi.isConnected()) {
    mqttReconnectTimer.once(2, connectToMqtt);
  }
}

// MQTT payload messages
char *sensorTopicsOn[] = {"test/1/on","test/2/on","test/3/on","test/4/on",
                          "test/5/on","test/6/on","test/7/on","test/8/on",
                          "test/9/on","test/10/on","test/11/on","test/12/on",
                          "test/13/on","test/14/on","test/15/on","test/16/on"};
                        
char *sensorTopicsOff[] = {"test/1/off","test/2/off","test/3/off","test/4/off",
                          "test/5/off","test/6/off","test/7/off","test/8/off",
                          "test/9/off","test/10/off","test/11/off","test/12/off",
                          "test/13/off","test/14/off","test/15/off","test/16/off"};

void setup() {
  Serial.begin(115200);
  // GPIO setup on expander
  Wire.begin(); // no address = join as master
  // sequence        GPIOA:76543210  B:76543210
  setPullUps(MCP_ADDR_1, 0b11111111, 0b11111111);

  // Auto-reconnect callbacks if WiFi drops
  wifiConnectHandler = WiFi.onStationModeGotIP(onWifiConnect);
  wifiDisconnectHandler = WiFi.onStationModeDisconnected(onWifiDisconnect);

  // MQTT server set and event callback
  mqttClient.setServer(MQTT_HOST, MQTT_PORT);
  mqttClient.onDisconnect(onMqttDisconnect);
  mqttClient.setClientId("Robot7StationB");
  
  // Connect to WiFi
  connectToWifi();

  // NTP setup
  NTP.begin("UMGSVRNTP.WORLD.BIZ", 0, true, 0);
}

// Publish and sensor variables
int QoS = 2;
bool retain = false;
bool inputs[16];
bool previousState[16] = {true, true, true, true, true, true, true, true,
                          true, true, true, true, true, true, true, true};
bool risingEdge[16] = {false, false, false, false, false, false, false, false,
                       false, false, false, false, false, false, false, false};
bool fallingEdge[16] = {false, false, false, false, false, false, false, false,
                       false, false, false, false, false, false, false, false};
bool published[16];
int stateCount[16];
char *payload;
int debounceCounter = 100; // debounce time delay = (this number * time it takes to execute 1 loop of program)

void loop() {
  // Sensors change-of-state MQTT publish events
  uint16_t allGPIO = readGPIO(MCP_ADDR_1);
  for (int a = 0; a < 16; a++) {
    ((allGPIO & (1 << a)) != 0) ? inputs[a] = 1: inputs[a] = 0; // read all GPIO states into array
    
    if (previousState[a] && !inputs[a]) { // rising edge on sniff signal (opposite logic here because pull-ups)
      risingEdge[a] = true;
      fallingEdge[a] = false;
      stateCount[a] = 0;
      published[a] = false;
    }
    if (!previousState[a] && inputs[a]) { // falling edge
      fallingEdge[a] = true;
      risingEdge[a] = false;
      stateCount[a] = 0;
      published[a] = false;
    }

    if (risingEdge[a] && !inputs[a]) { // sensor still ON after rising edge (pulling GPIO down)
      stateCount[a]++;
    }
    if (fallingEdge[a] && inputs[a]) { // sensor still OFF after falling edge (GPIO pulled up)
      stateCount[a]++;
    }

    if ((stateCount[a] > debounceCounter) && !published[a]) {
      // NTP time
      String strDt = NTP.getTimeDateString();
      strDt.toCharArray(payload, 20);
      
      if (risingEdge[a]) {
        mqttClient.publish(sensorTopicsOn[a], QoS, retain, payload);
      } else {
        mqttClient.publish(sensorTopicsOff[a], QoS, retain, payload);
      }
      published[a] = true;
    }

    previousState[a] = inputs[a];
  }
}
