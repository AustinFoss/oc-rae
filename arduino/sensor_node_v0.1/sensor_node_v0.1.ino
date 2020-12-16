// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// 
//  T = tmp = Temperature in Celsius: C (A3)
//  H = hum = Relative Humidity: % (A3)
//  M = mst = Soil Moisture: % (A2) 
//  L = lux = Ambient light levels: lux (A1)
//
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#include <LiquidCrystal_I2C.h>

#define VREF 5.0 // Operating V of tmp & hum sensor
#define ADC_RESOLUTION 1024
#define TEMPERATURE_PIN A3
#define HUMIDITY_PIN A2
#define LUX_PIN A1
#define SOIL_MOISTURE_PIN A0

// The IP address of the Raspberry Pi Zero sent to the Arduino
char ipAddress[15];

// LCD display settings
LiquidCrystal_I2C lcd(0x27,16,2); 

// Soil Moisture sensor callibration variables 
const int dryValue = 526; 
const int soakedValue = 256;
const float scaleValue = dryValue - soakedValue;

float tmp, hum, analogVolt, lux, mst;

void setup() {
  // Basic setup instructions for the USB connection & LCD display
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();
  lcd.clear();
}

void loop() {

  // If serial information received, & no IP address has been recorded
  //  Then print the IP address to the display
  if (Serial.available() > 0 && ipAddress[0] == 0) {
    Serial.readBytes(ipAddress, Serial.available());
    lcd.setCursor(0,0);
    lcd.print(ipAddress);
  }
  
  // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  // Read & calculate all sensor values
  mst = (1-((analogRead(SOIL_MOISTURE_PIN)-soakedValue)/scaleValue))*100;
  
  analogVolt = (float)analogRead(TEMPERATURE_PIN) / ADC_RESOLUTION * VREF;
  // Convert voltage to temperature (℃, centigrade)
  tmp = -66.875 + 72.917 * analogVolt;

  analogVolt = (float)analogRead(HUMIDITY_PIN) / ADC_RESOLUTION * VREF;
  // Convert voltage to relative humidity (%)
  hum = -12.5 + 41.667 * analogVolt;

  lux = analogRead(LUX_PIN);
  // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  // Send sensor data to the Raspberry Pi Zero over USB
  Serial.println();
  Serial.print("T");
  Serial.print(tmp);
  Serial.print("H");
  Serial.print(hum);
  Serial.print("L");
  Serial.print(lux);
  Serial.print("M");
  Serial.print(mst);

  // Print sensor data to the LCD display
  lcd.setCursor(0,1);
  lcd.print("T");
  lcd.print("   ");
  lcd.setCursor(1,1);
  lcd.print(round(tmp));
  lcd.setCursor(4,1);
  lcd.print("H");
  lcd.print("   ");
  lcd.setCursor(5,1);
  lcd.print(round(hum));
  lcd.setCursor(8,1);
  lcd.print("M");
  lcd.print("   ");
  lcd.setCursor(9,1);
  lcd.print(round(mst));
  lcd.setCursor(12,1);
  lcd.print("L");
  lcd.print("   ");
  lcd.setCursor(13,1);
  lcd.print(round(lux));
  
  delay(100);
  
}
