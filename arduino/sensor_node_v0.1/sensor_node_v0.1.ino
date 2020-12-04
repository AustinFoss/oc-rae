#include <LiquidCrystal_I2C.h>

#define VREF 5.0 // Operating V of tmp & hum sensor
#define ADC_RESOLUTION 1024
#define TEMPERATURE_PIN A3
#define HUMIDITY_PIN A2
#define LUX_PIN A1
#define SOIL_MOISTURE_PIN A0

LiquidCrystal_I2C lcd(0x27,16,2);

// Callibration variables 
const int dryValue = 526; 
const int soakedValue = 256;
const float scaleValue = dryValue - soakedValue;
char ipAddress[15];

float tmp, hum, analogVolt, lux, soilMoisture;

void setup() {
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();
  lcd.clear();
}

void loop() {

  if (Serial.available() > 0 && ipAddress[0] == 0) {
    Serial.readBytes(ipAddress, Serial.available());
    lcd.setCursor(0,0);
    lcd.print(ipAddress);
  }
  
  soilMoisture = (1-((analogRead(SOIL_MOISTURE_PIN)-soakedValue)/scaleValue))*100;
  
  analogVolt = (float)analogRead(TEMPERATURE_PIN) / ADC_RESOLUTION * VREF;
  // Convert voltage to temperature (℃, centigrade)
  tmp = -66.875 + 72.917 * analogVolt;

  analogVolt = (float)analogRead(HUMIDITY_PIN) / ADC_RESOLUTION * VREF;
  // Convert voltage to relative humidity (%)
  hum = -12.5 + 41.667 * analogVolt;

  lux = analogRead(LUX_PIN);

  Serial.print("T");
  Serial.print(tmp);
  Serial.print("H");
  Serial.print(hum);
  Serial.print("L");
  Serial.print(lux);
  Serial.print("M");
  Serial.print(soilMoisture);
  
  Serial.println();

  lcd.setCursor(0,1);
  lcd.print("T");
  lcd.print(round(tmp));
  lcd.setCursor(3,1);
  lcd.print(" ");
  lcd.print("H");
  lcd.print(round(hum));
  lcd.setCursor(7,1);
  lcd.print(" ");
  lcd.print("M");
  lcd.print(round(soilMoisture));
  lcd.setCursor(11,1);
  lcd.print(" ");
  lcd.print("L");
  lcd.print(round(lux));
  
  delay(1000);
  
}
