#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include <AccelStepper.h>
#include <MultiStepper.h>

//============================================================

//Motorshield object
Adafruit_MotorShield AFMS = Adafruit_MotorShield();

//Adafruit object
Adafruit_StepperMotor *altMotor = AFMS.getStepper(200, 2);   //(steps per rev., M1(1,2))
Adafruit_StepperMotor *azMotor = AFMS.getStepper(200, 1);    //(steps per rev., M2(3,4))

//Functies voor Accelstepper object
void azForwardStep(){
  azMotor->onestep(FORWARD, INTERLEAVE);
}//End azForwardStep
void azBackwardStep(){
  azMotor->onestep(BACKWARD, INTERLEAVE);
}//End azBackwardStep
void altForwardStep(){
  altMotor->onestep(FORWARD, INTERLEAVE);
}//End altForwardStep
void altBackwardStep(){
  altMotor->onestep(BACKWARD, INTERLEAVE);
}//End altBackwardStep

//Accelstepper object
AccelStepper altStepper(altForwardStep, altBackwardStep);
AccelStepper azStepper(azForwardStep, azBackwardStep);

//Multistepper object
MultiStepper steppers;

//============================================================

long timeout = 10;

const byte maxChars = 32;
char receivedChars[maxChars];
//Tijdelijke array, strtok() vernietigt oude, ( sectionMarker => NULL)
char tempChars[maxChars];                       

//Markers dat begin / einde / sectie van data aangeven
char startMarker = '<';    
char endMarker = '>';                                  
char sectionMarker[1] = "|"; 

//Variabelen voor doorgestuurde data
long altFromPC;
long azFromPC;

long positions[1];

boolean newData = false;                   

long prevAltFromPC = 0;
long prevAzFromPC = 0;

byte altMaxSpeed = 250;     //Steps / second
byte azMaxSpeed = 250;      //Steps / second

byte altAcceleration = 200;
byte azAcceleration = 200;
//============================================================

void setup(){
  Serial.begin(9600);
  //Als timeout (ms) verlopen is, stop met lezen van string
  Serial.setTimeout(timeout);

  AFMS.begin();

  //Setting max speed
  altStepper.setMaxSpeed(altMaxSpeed); 
  azStepper.setMaxSpeed(azMaxSpeed);  

  //Setting acceleration
  altStepper.setAcceleration(altAcceleration);
  azStepper.setAcceleration(azAcceleration);

  //Adding steppers
  steppers.addStepper(altStepper);
  steppers.addStepper(azStepper);
}//End setup

//============================================================

void loop(){
  receiveData();    //Nieuwe data nemen
  newData = false;  //Nu is het niet nieuw meer
  parseData();      //Splits de gekregen data
  

  positions[0] = altFromPC;//altFromPC
  positions[1] = azFromPC;//azFromPC

  
  steppers.moveTo(positions); 
  steppers.run();
}//End loop

//============================================================

void receiveData(){
  static boolean recvInProgress = false; 
  static byte i = 0;
  char data;

  while (Serial.available() > 0 && newData == false){
    data = Serial.read();

    if (data == startMarker){
      recvInProgress = true;
    } else if (recvInProgress == true) {
      if (data != endMarker){
        receivedChars[i] = data;
        i++;
        if (i >= maxChars){
          i = maxChars - 1;
        }//End if
      } else {
        receivedChars[i] = '\0';  //Eindig de string met NULL
        recvInProgress = false;
        i = 0;
        newData = true;
      }//End if else
    }//End if / else if
  }//End while loop
}//End receiveData

//============================================================

void parseData(){
  char * strtokIndex;                               //strtok() gebruikt dit als index

  strcpy(tempChars, receivedChars);                 //Copieer receivedChars naar tempChars

  strtokIndex = strtok(tempChars, sectionMarker);   //Neem 1ste deel van de data
  altFromPC = atol(strtokIndex);                    //Sla het op in altFromPC

  strtokIndex = strtok(NULL, sectionMarker);        //Doet voort waar hij gestopt was
  azFromPC = atol(strtokIndex);                     //Sla het op in azFromPC
}//End parseData
