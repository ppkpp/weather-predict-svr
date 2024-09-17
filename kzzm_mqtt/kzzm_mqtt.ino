#include <WiFi.h>
#include <LiquidCrystal_I2C.h>
#include "DHT.h"
#include <PubSubClient.h>
#include "CO2Sensor.h"
#include <HTTPClient.h>

// CO2 sensor setup
CO2Sensor co2Sensor(10, 0.99, 100);
#define DHTPIN 18
#define DHTTYPE DHT11

// LCD setup
LiquidCrystal_I2C lcd(0x27, 16, 2);  // 16x2 LCD

// WiFi credentials
const char* ssid = "Khaing Zar";
const char* password = "kzzm12345";

// DHT sensor setup
DHT dht(DHTPIN, DHTTYPE);

// Common server IP address
const char* serverIP = "13.214.222.110"; // Replace with your server's IP
const char* mqtt_server = "13.214.222.110";
const int mqtt_port = 1883;
const char* topic = "iot/message";
WiFiClient espClient;
PubSubClient client(espClient);

// HTTP endpoint and Socket.IO port
const int socketPort = 8888;  // Socket.IO server port
const String httpUrl = String("http://") + serverIP + ":8000/sensors";  // HTTP POST endpoint

// Timing variables for data sending
unsigned long lastSendTime = 0;
unsigned long lastSocketTime = 0;  // Added for Socket.IO message control
const unsigned long interval = 3600000;  // 1 hour (3600000 milliseconds)
const unsigned long socketInterval = 5000;  // 5 seconds for Socket.IO messages

// Function to display messages on the LCD
void showMessage(String line1, String line2) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(line1);
  lcd.setCursor(0, 1);
  lcd.print(line2);
}

// Function to connect to WiFi
void wifiConnect() {
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConnected to WiFi");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nFailed to connect to WiFi");
    // Optionally reset the ESP32 if WiFi connection fails
    ESP.restart();
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32Client")) {
      Serial.println("Connected");
      showMessage("MQTT", "connected");
      client.subscribe(topic);  // Subscribe to topic if needed
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" Try again in 5 seconds");
      delay(5000);
    }
  }
}

// Function to send data to the HTTP server
void sendToServer(String temp, String humidity, String rtc, String node, String carbon) {
  HTTPClient http;
  http.begin(httpUrl);  
  http.addHeader("Content-Type", "application/json");

  // Create the JSON payload
  String jsonPayload = "{\"temperature\":\"" + temp + "\",\"humidity\":\"" + humidity + "\",\"createdate\":\"" + rtc + "\",\"node\":\"" + node + "\",\"carbon\":\"" + carbon + "\"}";

  // Send the POST request
  int httpResponseCode = http.POST(jsonPayload);

  if (httpResponseCode > 0) {
    String response = http.getString();       
    Serial.println("HTTP Response code: " + String(httpResponseCode));   
    Serial.println("Response: " + response);
  } else {
    Serial.print("Error on sending POST: ");
    Serial.println(httpResponseCode);
  }
  http.end();
}

void setup() {
  // Serial communication for debugging
  Serial.begin(9600);
  
  // CO2 sensor calibration
  co2Sensor.calibrate();

  // LCD initialization
  lcd.init();
  lcd.backlight();
  showMessage("IOT Device", "Connecting to WiFi");

  // Initialize DHT sensor
  dht.begin();

  // Connect to WiFi
  wifiConnect();
  showMessage("IOT Device", "Connected");

  client.setServer(mqtt_server, mqtt_port);
  reconnect(); 
}

void loop() {
  unsigned long currentMillis = millis();

  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Read CO2 sensor value
  int val = co2Sensor.read();

  // Read DHT sensor values
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  float f = dht.readTemperature(true);  // Fahrenheit

  // Get the RTC timestamp (replace with actual RTC or NTP timestamp)
  String rtc = "2024-09-15 12:00:00";  // Placeholder value, use actual RTC or NTP timestamp

  // Check if DHT sensor values are valid
  if (isnan(h) || isnan(t) || isnan(f)) {
    Serial.println(F("Failed to read from DHT sensor!"));
    return;
  }

  // Display the current sensor values on the LCD
  showMessage("Temp: " + String(f) + "*C", "Humidity: " + String(h) + "%");

  // Check if 1 hour has passed since the last data send to HTTP server
  if (currentMillis - lastSendTime >= interval) {
    Serial.println("Sending data to HTTP server...");

    // Send data to HTTP server
    sendToServer(String(t), String(h), rtc, "node1", String(val));  // Send to HTTP

    // Update the last send time for HTTP
    lastSendTime = currentMillis;

    // Show success message on the LCD
    showMessage("Sent to server", "Success");
  }

  // Check if 5 seconds have passed since the last data send to MQTT
  if (currentMillis - lastSocketTime >= socketInterval) {
    Serial.println("Sending data to MQTT server...");

    // Prepare JSON payload for MQTT
    String payload = "{\"temp\":\"" + String(t) + "\",\"humidity\":\"" + String(h) + "\",\"node\":\"node1\",\"carbon\":\"" + String(val) + "\"}";

    // Send data to MQTT server
    if (client.connected()) {
      client.publish(topic, payload.c_str());
      Serial.println("Data sent to MQTT: " + payload);
    } else {
      Serial.println("MQTT not connected");
    }

    // Update the last send time for MQTT
    lastSocketTime = currentMillis;
  }

  // Short delay to prevent looping too fast
  delay(1000);
}
