//*========================================
// *notation*
// This version's MPU initialized the scale "+-2000dps" and "+-16g"
// It can affect your device condition
// The Helmet Blackbox Project <<SCOOKER>>
// When you turn on the Device, it will be automatically Calibration about least 2 min.
// So, Release the device on the flat place.
// Written by GMObean
//*========================================

#include <SoftwareSerial.h> 
#include <string.h>

#include "Wire.h"
#include "I2Cdev.h"
#include "MPU9250.h"
#define VERSION "0.0.1"

// class default I2C address is 0x68
// specific I2C addresses may be passed as a parameter here
// AD0 low = 0x68 (default for InvenSense evaluation board)
// AD0 high = 0x69
MPU9250 accelgyro;
I2Cdev   I2C_M;

void get_one_sample_date_mxyz();
void getAccel_Data(void);
void getGyro_Data(void);
void getCompass_Data(void);
void getCompassDate_calibrated ();
void setLEDColor(int, int, int);

uint8_t buffer_m[6];

int16_t ax, ay, az;
int16_t gx, gy, gz;
int16_t mx, my, mz;

float heading;
float tiltheading;

float Axyz[3];
float Gxyz[3];
float Mxyz[3];

#define sample_num_mdate  5000

volatile float mx_sample[3];
volatile float my_sample[3];
volatile float mz_sample[3];

static float mx_centre = 0;
static float my_centre = 0;
static float mz_centre = 0;

volatile int mx_max = 0;
volatile int my_max = 0;
volatile int mz_max = 0;

volatile int mx_min = 0;
volatile int my_min = 0;
volatile int mz_min = 0;

float temperature;
float pressure;
float atm;
float altitude;

// Measurement Parameter
 /** Get full-scale gyroscope range.
 * The FS_SEL parameter allows setting the full-scale range of the gyro sensors,
 * as described in the table below.
 *
 * <pre>
 * 0 = +/- 250 degrees/sec
 * 1 = +/- 500 degrees/sec
 * 2 = +/- 1000 degrees/sec
 * 3 = +/- 2000 degrees/sec
 * </pre>
 *
 * @return Current full-scale gyroscope range setting
 * @see MPU9250_GYRO_FS_250
 * @see MPU9250_RA_GYRO_CONFIG
 * @see MPU9250_GCONFIG_FS_SEL_BIT
 * @see MPU9250_GCONFIG_FS_SEL_LENGTH
 */
 int Gyro_scale = 2000;
 
/** Get full-scale accelerometer range.
 * The FS_SEL parameter allows setting the full-scale range of the accelerometer
 * sensors, as described in the table below.
 *
 * <pre>
 * 0 = +/- 2g
 * 1 = +/- 4g
 * 2 = +/- 8g
 * 3 = +/- 16g
 * </pre>
 *
 * @return Current full-scale accelerometer range setting
 * @see MPU9250_ACCEL_FS_2
 * @see MPU9250_RA_ACCEL_CONFIG
 * @see MPU9250_ACONFIG_AFS_SEL_BIT
 * @see MPU9250_ACONFIG_AFS_SEL_LENGTH
 */
int Accel_scale = 16;

// PIN info
// Gyro_SCL = A5
// Gyro_SDA = A4
int BT_TX = 2;
int BT_RX = 3;

int VIB_UP = 5;
int VIB_DOWN = 7;
int VIB_LEFT = 4;
int VIB_RIGHT = 6;

int STATUS_RED = 9;
int STATUS_GREEN = 10;
int STATUS_BLUE = 11;

bool Vudlr[4];
bool Vudlr_goal[4];
char DataString[62];
char accellist[19];   //******a******a******a
char gyrolist[25];    //********a********a********a 
char compasslist[19]; //******a******a******a
String bt_buffer = "0000";

// Bluetooth Setting
SoftwareSerial BTSerial(BT_TX, BT_RX); // Software Serial (TX,RX) 

// Timer Setting
static long analogPinTimer = 0; // 1) 
#define ANALOG_PIN_TIMER_INTERVAL 1000000// 2) 
unsigned long thisMicros_old; // 3)

void setup(){
  Wire.begin();
  Serial.begin(38400);  // 통신속도 38400 bps
  BTSerial.begin(9600);
  char FWversion[10] = VERSION;
  BTSerial.write(FWversion);
  BTSerial.write('\n');
  pinMode(STATUS_RED,OUTPUT);
  pinMode(STATUS_GREEN,OUTPUT);
  pinMode(STATUS_BLUE,OUTPUT);
  
  pinMode(VIB_UP,OUTPUT);
  pinMode(VIB_DOWN,OUTPUT);
  pinMode(VIB_LEFT,OUTPUT);
  pinMode(VIB_RIGHT,OUTPUT);

  //Firmware Info
  Serial.print("SCOOKER Firmware| ");
  Serial.println(FWversion);
  Serial.println("Initializing I2C devices...");
  accelgyro.initialize();
  // verify connection
  Serial.println("Testing device connections...");
  Serial.println(accelgyro.testConnection() ? "MPU9250 connection successful" : "MPU9250 connection failed");

  /*
  // verify LED connection
  setLEDColor(255,255,255);
  delay(2000);
  setLEDColor(255,0,0);
  delay(200);
  setLEDColor(0,255,0);
  delay(200);
  setLEDColor(0,0,255);
  delay(200);
  setLEDColor(0,0,0);
  */
}

void loop(){
  String buf;
  while (BTSerial.available()) {
    char c = BTSerial.read();
    buf += c;
  }
  if (buf.length() > 4){
    for(int i=0; i<4; i++){bt_buffer[i]=buf[i];}
  }
  Serial.print("Bluetooth IN: ");
  Serial.println(bt_buffer);
  
  getAccel_Data();
  getGyro_Data();
  getSendingData();
  getCompassDate_calibrated(); // compass data has been calibrated here
  getHeading();               //before we use this function we should run 'getCompassDate_calibrated()' frist, so that we can get calibrated data ,then we can get correct angle .
  getTiltHeading(); 
  getVibratorState();
  setVibrator();
  printGyroDataBySerial();
  printVibDataBySerial();
  BTSerial.write(accellist);
  BTSerial.write(bt_buffer[0]);
  BTSerial.write('\n');
  
  delay(5);
}
// ******************************************************** Test Method ***********************************************************************************
void printHeadingDataBySerial(){
  Serial.print("Heading Value: ");
  Serial.print(heading);
  Serial.print(',');
  Serial.println(tiltheading);
}

void printVibDataBySerial(){
  Serial.print("Vibration State: ");
  Serial.print(Vudlr[0]);
  Serial.print(Vudlr[1]);
  Serial.print(Vudlr[2]);
  Serial.println(Vudlr[3]);
}

void printGyroDataBySerial(){
    Serial.println("Acceleration(g) of X,Y,Z:");
    Serial.print(Axyz[0]);
    Serial.print(",");
    Serial.print(Axyz[1]);
    Serial.print(",");
    Serial.println(Axyz[2]);
    /*
    Serial.println("Angular Velocity (Degree per sec) of X,Y,Z:");
    Serial.print(Gxyz[0]);
    Serial.print(",");
    Serial.print(Gxyz[1]);
    Serial.print(",");
    Serial.println(Gxyz[2]);
    */
    /*
    //Serial.println("Campass (Degree) of X,Y,Z:");
    Serial.print(Mxyz[0]);
    Serial.print(",");
    Serial.print(Mxyz[1]);
    Serial.print(",");
    Serial.println(Mxyz[2]);
    */
}


// ********************************************************RGB LED Control Method ***********************************************************************************

void setLEDColor(int red, int green, int blue){
    analogWrite(STATUS_RED, 255-red);
    analogWrite(STATUS_GREEN, 255-green);
    analogWrite(STATUS_BLUE, 255-blue);
    delay(10);
}

// ********************************************************Vibrator Control Method ***********************************************************************************
void getVibratorState(void){
  // longitudinal: Y-axis
  if ((1.20 > Axyz[2]) && (Axyz[2] > 0.70)){Vudlr[0] = true; Vudlr[1] = false;}
  if ((-1.20 < Axyz[2]) && (Axyz[2] < -0.70)){Vudlr[0] = false; Vudlr[1] = true;}
  if ((1.20 > Axyz[1]) && (Axyz[1] > 0.70)){Vudlr[2] = true; Vudlr[3] = false;}
  if ((-1.20 < Axyz[1]) && (Axyz[1] < -0.70)){Vudlr[2] = false; Vudlr[3] = true;}
  /*
  for(int i=0; i<4; i++){
    if (bt_buffer[i] == '1'){Vudlr[i] = true;}
    else if (bt_buffer[i] == '0'){Vudlr[i] = false;}
  }
  */
}

void setVibrator(void){
    if (Vudlr[0]){digitalWrite(VIB_UP, HIGH);}
    else{digitalWrite(VIB_UP, LOW);}
    if (Vudlr[1]){digitalWrite(VIB_DOWN, HIGH);}
    else{digitalWrite(VIB_DOWN, LOW);}
    if (Vudlr[2]){digitalWrite(VIB_LEFT, HIGH);}
    else{digitalWrite(VIB_LEFT, LOW);}
    if (Vudlr[3]){digitalWrite(VIB_RIGHT, HIGH);}
    else{digitalWrite(VIB_RIGHT, LOW);}
}

// ********************************************************Data Protocol Method ***********************************************************************************


void getSendingData(void){
    int int_Axyz[3] = {0};
    int int_Gxyz[3] = {0};
    int int_Mxyz[3] = {0};

    int i = 0;
    // Float data to char
    for(i=0; i < 3; i++){
    int_Axyz[i] = Axyz[i]*100;
    int_Gxyz[i] = Gxyz[i]*100;
    int_Mxyz[i] = Mxyz[i]*100;
    }

    char partition_char = 'a';

    for(i=0; i < 3; i++){
      accellist[i*6+5] = partition_char;
      gyrolist[i*8+7] = partition_char;
      compasslist[i*6+5] = partition_char;
    }

    // Define sign of number
    for(i=0; i < 3; i++){
      if(int_Axyz[i] > 0){accellist[i*6]='0';}
      else {accellist[i*6]= '1';}
      if(int_Gxyz[i] > 0){gyrolist[i*8]='0';}
      else {gyrolist[i*8]= '1';}
      if(int_Mxyz[i] > 0){compasslist[i*6]='0';}
      else {compasslist[i*6]= '1';}
    }
    
    for(i=0; i < 3; i++){
      int_Axyz[i] = abs(int_Axyz[i]);
      int_Gxyz[i] = abs(int_Gxyz[i]);
      int_Mxyz[i] = abs(int_Mxyz[i]);
    }

    for(i=0; i < 3; i++){
      accellist[i*6+1] = int_Axyz[i]/1000 + '0';
      int_Axyz[i] = int_Axyz[i] - (int_Axyz[i]/1000)*1000;
      accellist[i*6+2] = int_Axyz[i]/100 + '0';
      int_Axyz[i] = int_Axyz[i] - (int_Axyz[i]/100)*100;
      accellist[i*6+3] = int_Axyz[i]/10 + '0';
      int_Axyz[i] = int_Axyz[i] - (int_Axyz[i]/10)*10;
      accellist[i*6+4] = int_Axyz[i] + '0';

      gyrolist[i*8+1] = int_Gxyz[i]/100000 + '0';
      int_Gxyz[i] = int_Gxyz[i] - (int_Gxyz[i]/100000)*100000;
      gyrolist[i*8+2] = int_Gxyz[i]/10000 + '0';
      int_Gxyz[i] = int_Gxyz[i] - (int_Gxyz[i]/10000)*10000;
      gyrolist[i*8+3] = int_Gxyz[i]/1000 + '0';
      int_Gxyz[i] = int_Gxyz[i] - (int_Gxyz[i]/1000)*1000;
      gyrolist[i*8+4] = int_Gxyz[i]/100 + '0';
      int_Gxyz[i] = int_Gxyz[i] - (int_Gxyz[i]/100)*100;
      gyrolist[i*8+5] = int_Gxyz[i]/10 + '0';
      int_Gxyz[i] = int_Gxyz[i] - (int_Gxyz[i]/10)*10;
      gyrolist[i*8+6] = int_Gxyz[i] + '0';

      compasslist[i*6+1] = int_Mxyz[i]/1000 + '0';
      int_Mxyz[i] = int_Mxyz[i] - (int_Mxyz[i]/1000)*1000;
      compasslist[i*6+2] = int_Mxyz[i]/100 + '0';
      int_Mxyz[i] = int_Mxyz[i] - (int_Mxyz[i]/100)*100;
      compasslist[i*6+3] = int_Mxyz[i]/10 + '0';
      int_Mxyz[i] = int_Mxyz[i] - (int_Mxyz[i]/10)*10;
      compasslist[i*6+4] = int_Mxyz[i] + '0';
    }
    
    //Serial.println("Sending Data: ");
    /*
    Serial.print(accellist);
    Serial.print(gyrolist);
    Serial.println(compasslist);
    */

    for(i=0; i < 18; i++){
      DataString[i]=accellist[i];
    }
    for(i=0; i < 24; i++){
      DataString[i+18]=gyrolist[i];
    }
    for(i=0; i < 18; i++){
      DataString[i+42]=compasslist[i];
    }
}

// ********************************************************MPU9250(Gyro sensor) Method ***********************************************************************************

void getHeading(void)
{
    heading = 180 * atan2(Mxyz[1], Mxyz[0]) / PI;
    if (heading < 0) heading += 360;
}
void getTiltHeading(void)
{
    float pitch = asin(-Axyz[0]);
    float roll = asin(Axyz[1] / cos(pitch));

    float xh = Mxyz[0] * cos(pitch) + Mxyz[2] * sin(pitch);
    float yh = Mxyz[0] * sin(roll) * sin(pitch) + Mxyz[1] * cos(roll) - Mxyz[2] * sin(roll) * cos(pitch);
    float zh = -Mxyz[0] * cos(roll) * sin(pitch) + Mxyz[1] * sin(roll) + Mxyz[2] * cos(roll) * cos(pitch);
    tiltheading = 180 * atan2(yh, xh) / PI;
    if (yh < 0)    tiltheading += 360;
}
void Mxyz_init_calibrated ()
{

    Serial.println(F("Before using 9DOF,we need to calibrate the compass frist,It will takes about 2 minutes."));
    Serial.print("  ");
    Serial.println(F("During  calibratting ,you should rotate and turn the 9DOF all the time within 2 minutes."));
    Serial.print("  ");
    Serial.println(F("If you are ready ,please sent a command data 'ready' to start sample and calibrate."));
    //while (!Serial.find("ready"));
    Serial.println("  ");
    Serial.println("ready");
    Serial.println("Sample starting......");
    Serial.println("waiting ......");

    get_calibration_Data ();

    Serial.println("     ");
    Serial.println("compass calibration parameter ");
    Serial.print(mx_centre);
    Serial.print("     ");
    Serial.print(my_centre);
    Serial.print("     ");
    Serial.println(mz_centre);
    Serial.println("    ");
}
void get_calibration_Data ()
{
    for (int i = 0; i < sample_num_mdate; i++)
    {
        get_one_sample_date_mxyz();

        if (mx_sample[2] >= mx_sample[1])mx_sample[1] = mx_sample[2];
        if (my_sample[2] >= my_sample[1])my_sample[1] = my_sample[2]; //find max value
        if (mz_sample[2] >= mz_sample[1])mz_sample[1] = mz_sample[2];

        if (mx_sample[2] <= mx_sample[0])mx_sample[0] = mx_sample[2];
        if (my_sample[2] <= my_sample[0])my_sample[0] = my_sample[2]; //find min value
        if (mz_sample[2] <= mz_sample[0])mz_sample[0] = mz_sample[2];
    }
    mx_max = mx_sample[1];
    my_max = my_sample[1];
    mz_max = mz_sample[1];

    mx_min = mx_sample[0];
    my_min = my_sample[0];
    mz_min = mz_sample[0];
    
    mx_centre = (mx_max + mx_min) / 2;
    my_centre = (my_max + my_min) / 2;
    mz_centre = (mz_max + mz_min) / 2;
}
void get_one_sample_date_mxyz()
{
    getCompass_Data();
    mx_sample[2] = Mxyz[0];
    my_sample[2] = Mxyz[1];
    mz_sample[2] = Mxyz[2];
}
void getAccel_Data(void)
{
    accelgyro.getMotion9(&ax, &ay, &az, &gx, &gy, &gz, &mx, &my, &mz);
    Axyz[0] = (double) ax * Accel_scale / 32768;
    Axyz[1] = (double) ay * Accel_scale / 32768;
    Axyz[2] = (double) az * Accel_scale / 32768;
}
void getGyro_Data(void)
{
    accelgyro.getMotion9(&ax, &ay, &az, &gx, &gy, &gz, &mx, &my, &mz);

    Gxyz[0] = (double) gx * Gyro_scale / 32768;
    Gxyz[1] = (double) gy * Gyro_scale / 32768;
    Gxyz[2] = (double) gz * Gyro_scale / 32768;
}
void getCompass_Data(void)
{
    I2C_M.writeByte(MPU9150_RA_MAG_ADDRESS, 0x0A, 0x01); //enable the magnetometer
    delay(10);
    I2C_M.readBytes(MPU9150_RA_MAG_ADDRESS, MPU9150_RA_MAG_XOUT_L, 6, buffer_m);

    mx = ((int16_t)(buffer_m[1]) << 8) | buffer_m[0] ;
    my = ((int16_t)(buffer_m[3]) << 8) | buffer_m[2] ;
    mz = ((int16_t)(buffer_m[5]) << 8) | buffer_m[4] ;

    Mxyz[0] = (double) mx * 1200 / 4096;
    Mxyz[1] = (double) my * 1200 / 4096;
    Mxyz[2] = (double) mz * 1200 / 4096;
}
void getCompassDate_calibrated ()
{
    getCompass_Data();
    Mxyz[0] = Mxyz[0] - mx_centre;
    Mxyz[1] = Mxyz[1] - my_centre;
    Mxyz[2] = Mxyz[2] - mz_centre;
}

 
