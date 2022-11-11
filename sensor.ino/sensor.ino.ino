#include <ESP8266HTTPClient.h>
#include <ESP8266WiFi.h>
#include "DHT.h"

WiFiClient wifi;
DHT dht(5, DHT11);

void setup() {
  Serial.begin(9600);
  WiFi.begin("Matka Boska", "Zbawienie420");

  while (WiFi.status() != WL_CONNECTED) {
 
    delay(500);
    Serial.print(".");
 
  }
  dht.begin();
}
 
void loop() {
  
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  if (isnan(h) || isnan(t)) {
    Serial.println(F("Failed to read from DHT sensor!"));
    delay(5000);
    return;
  }

  if (WiFi.status() == WL_CONNECTED) {
 
    HTTPClient http;
 
    http.begin(wifi, "http://192.168.2.11:5000/request/");
    http.addHeader("Content-Type", "text/plain");
 
    int httpCode = http.POST("{\"temperature\":\"" + String(t) + "\",\"humidity\":\"" + String(h) + "\"}");
    String payload = http.getString();
 
    Serial.println("temp: "+String(t)+"wilg: "+String(h));
    Serial.println(httpCode);
    Serial.println(payload);
 
    http.end();
 
  } else {
    Serial.println("Error in WiFi connection");
  }
  delay(30000);
}