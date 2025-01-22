#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <Adafruit_BMP085.h>

#define DHTPIN D5            // Sensörümüzün sinyal bacağının bağlı olduğu pini belirliyoruz.
#define DHTTYPE DHT11   

DHT dht(DHTPIN, DHTTYPE); 
Adafruit_BMP085 bmp;

// WiFi Ayarları

const char* ssid = "user";          // WiFi adınızı yazın
const char* password = "password";    // WiFi şifrenizi yazın

// MQTT Broker Ayarları
const char* mqtt_server = "192.168.1.22";  // MQTT Broker IP adresi (Python veya Mosquitto'nun çalıştığı makine)
const int mqtt_port = 1883;                 // MQTT portu
const char* mqtt_topic = "sera/veriler";    // MQTT konusu

WiFiClient espClient;
PubSubClient client(espClient);



struct Sensors{
  const char * sensor_id;
  float temp_1;
  float temp_2;
  float humidity;
  uint8_t water_level;
  int32_t pressure;
  float altitude;
  int32_t sea_level_pressure;

  Sensors(const char * _id = "sensor_1")
  {
    sensor_id = _id;
  }

  void readSensors(DHT* dht_ptr, Adafruit_BMP085* bmp_ptr)
  {
      temp_1 = dht_ptr->readTemperature();
      temp_2 = bmp_ptr->readTemperature();
      humidity = dht_ptr->readHumidity();
      water_level = analogRead(A0);
      pressure = bmp_ptr->readPressure();
      altitude = bmp_ptr->readAltitude();
      sea_level_pressure = bmp_ptr->readSealevelPressure();
  }

  String getPayload(void) const
  {
      String payload = "{";
      payload += "\"device_id\": \"sera_cihaz_1\", ";
      payload += "\"temperature_1\": " + String(temp_1) + ", ";
      payload += "\"temperature_2\": " + String(temp_2) + ", ";
      payload += "\"humidity\": " + String(humidity) + ", ";
      payload += "\"water_level\": " + String(water_level) + ", ";
      payload += "\"pressure\": " + String(pressure) + ", ";
      payload += "\"altitude\": " + String(altitude) + ", ";
      payload += "\"sea_level_pressure\": " + String(sea_level_pressure);
      payload += "}";

      return payload;
  }
};

Sensors sensor{"sensor_1"};

void reconnect() {
  // MQTT'ye yeniden bağlanana kadar deneme yap
  while (!client.connected()) {
    Serial.print("MQTT'ye bağlanılıyor...");
    if (client.connect("ESP8266Client")) {  // MQTT istemci kimliği
      Serial.println("Bağlandı!");
    } else {
      Serial.print("Bağlanma hatası, kod: ");
      Serial.print(client.state());
      Serial.println(". Yeniden deneme 5 saniye sonra.");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin(); 
  bmp.begin();
  pinMode(D7, OUTPUT);

  // WiFi'ye bağlanma
  Serial.println();
  Serial.print("WiFi'ye bağlanılıyor...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nWiFi'ye bağlandı!");
  Serial.print("IP adresi: ");
  Serial.println(WiFi.localIP());
  digitalWrite(D7, HIGH);

  // MQTT Broker'a bağlanma
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  sensor.readSensors(&dht, &bmp);
  String payload = sensor.getPayload();
  if (client.publish(mqtt_topic, payload.c_str())) {
    Serial.println("MQTT mesajı gönderildi:");
    Serial.println(payload);
  } else {
    Serial.println("MQTT mesajı gönderilemedi.");
  }

  delay(600);
}