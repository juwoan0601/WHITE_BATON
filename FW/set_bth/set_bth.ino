#include <SoftwareSerial.h>

int TX_BLE = 2; 
int RX_BLE = 3;

SoftwareSerial BTSerial(TX_BLE, RX_BLE); //아두이노 D2에 TXD, D3에 RXD를 연결 
 
void setup()  
{
  Serial.begin(9600); 
  BTSerial.begin(9600);
}
void loop()
{
  if (BTSerial.available())
   Serial.write(BTSerial.read());
  
  if (Serial.available())
   BTSerial.write(Serial.read()); 
}
