/*  Pressure Sensor to measure suction and controle pump
    University Leiden Fsw-Solo Evert 2022

   20221116 1.0 Beta test hardware concept. 
*/
  


#include "ADS1X15.h"  //https://github.com/RobTillaart/ADS1X15


ADS1115 ADS(0x48);  //I2c address
#define SW_auto 12
#define SW_manual 13
#define SPEEDPOT 0
#define PUMP 5 //Stond op 9?
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


void loop()
{
  int PressureValue = ADS.readADC_Differential_2_3();
  Serial.print(millis());
  Serial.print(";");
  Serial.print(Pumping);
  Serial.print(";");
  Serial.println(PressureValue);

  switch (checkswitch()) {
    case OFF:
      PumpPwm( 0);
      break;
    case MANUAL:
     PumpPwm(analogRead(SPEEDPOT) >> 2);
      break;
    case AUTO:
      if ((PressureValue < ZeroOffset - LOWERBOUNDERY) || (PressureValue > ZeroOffset + UPPERBOUNDERY)) {
        StartTime = millis();
        if (PumpIsRunning == false) {
          PumpIsRunning = true;
        }
      }
      break;
    default:
      break;
  }

  if (PumpIsRunning == true) {
    if (StartTime + PUMPTIME > millis()) {
      PumpPwm(analogRead(SPEEDPOT) >> 2);
    }
    else {
      PumpPwm(0);
      PumpIsRunning = false;
    }
  }

}

void PumpPwm(byte speed){
  analogWrite(PUMP, speed);
  if (speed==0){
    Pumping="F";
  }
  else{
    Pumping="T";
  }
}



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