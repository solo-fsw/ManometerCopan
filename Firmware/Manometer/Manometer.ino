


#include "ADS1X15.h"  //https://github.com/RobTillaart/ADS1X15


ADS1115 ADS(0x48);
#define SW_auto 12
#define SW_manual 13
#define SPEEDPOT 0
#define PUMP 9
#define MANUAL 1
#define AUTO 2
#define OFF 0

void setup()
{
  pinMode(SW_manual, INPUT_PULLUP);
  pinMode(SW_auto, INPUT_PULLUP);
  Serial.begin(115200);
  Serial.println(__FILE__);
  Serial.print("ADS1X15_LIB_VERSION: ");
  Serial.println(ADS1X15_LIB_VERSION);

  ADS.begin();
  ADS.setGain(16);      // 0.256V volt
  ADS.setDataRate(7);  // fast
  ADS.setMode(0);      // continuous mode
  ADS.readADC(0);      // first read to trigger
}


void loop()
{
  Serial.println(ADS.readADC_Differential_2_3());
  // optional other code here
  //delay(100);
 analogWrite(PUMP, analogRead(SPEEDPOT)>> 2);
}


// -- END OF FILE --

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
