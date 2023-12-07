/*  Pressure Sensor to measure suction and controle pump
    University Leiden Fsw-Solo Evert and Jens

   20221116 1.0 Beta test hardware concept. 
*/

// Definitions // ================================================================
#include "ADS1X15.h"  //https://github.com/RobTillaart/ADS1X15

ADS1115 ADS(0x48);  //I2c address
#define SW_auto 12
#define SW_manual 13
#define SPEEDPOT 0
#define PUMP 5
#define ALERT 8
#define MANUAL 1
#define AUTO 2
#define OFF 0
#define UPPERBOUNDERY 100
#define LOWERBOUNDERY 100
#define PUMPTIME 1000 //msec

int ZeroOffset = 0;
boolean PumpIsRunning = false;
unsigned long StartTime = 0;
String Pumping = "U" ;

// Setup // ================================================================
void setup()
{
  pinMode(SW_manual, INPUT_PULLUP);
  pinMode(SW_auto, INPUT_PULLUP);
  Serial.begin(115200);
  ADS.begin();
  ADS.setGain(16);      // 0.256V volt
  ADS.setDataRate(7);  // fast
  ADS.setMode(0);      // continuous mode
  ADS.readADC(0);      // first read to trigger
  ZeroOffset = CalibrateZero();
}

// Loop // ================================================================
void loop()
{
  int PressureValue = ADS.readADC_Differential_2_3();
  Serial.print(millis());
  Serial.print(";");
  Serial.print(Pumping);
  Serial.print(";");
  Serial.print(analogRead(SPEEDPOT) >> 2);
  Serial.print(";");
  Serial.println(PressureValue);

  switch (checkswitch()) {
    case OFF:
      analogWrite(PUMP, 0);
      Pumping = "F";
      break;
    case MANUAL:
     analogWrite(PUMP, analogRead(SPEEDPOT) >> 2);
     Pumping = "T";
      break;
    case AUTO:
      if (PressureValue < ZeroOffset - LOWERBOUNDERY) {
        StartTime = millis();
        if (PumpIsRunning == false) {
          PumpIsRunning = true;
        }
      }
      else {
        Pumping = "U";
      }

    if (PumpIsRunning == true) {
      if (StartTime + PUMPTIME > millis()) {
        analogWrite(PUMP, analogRead(SPEEDPOT) >> 2);
        Pumping = "T";
      } else {
        analogWrite(PUMP, 0);
        PumpIsRunning = false;
      }
    }
      break;
    default:
      break;
  }
}

// Helper functions // ================================================================
byte checkswitch() {
  if (digitalRead(SW_manual) == false) {
    return MANUAL;
  }
  if (digitalRead(SW_auto) == false) {
    return AUTO;
  }
  if (digitalRead(SW_manual) && digitalRead(SW_auto)) {
    return OFF;
  }
}

int CalibrateZero() {
  int avarage = 0;
  for (int i = 1; i <= 10; i++) {
    avarage += ADS.readADC_Differential_2_3();
    delay(100);
  }
  return avarage / 10;
}