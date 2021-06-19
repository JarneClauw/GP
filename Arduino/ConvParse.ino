//**// AANGEPAST VOORBEELD //**//

//====================

const byte maxChars = 32;
char receivedChars[maxChars];
char tempChars[maxChars];       //Tijdelijke array, strtok() vernietigt oude, ( sectionMarker => NULL)

//Markers dat begin / einde / sectie van data aangeven
char startMarker = '<';         //Moet char zijn
char endMarker = '>';           // ||   ||   || 
char sectionMarker[1] = "|";    //Moet char array zijn

//Variabelen voor doorgestuurde data
long altFromPC;
long azFromPC;

boolean newData = false;       //Is er nieuwe data?

//====================

void setup(){
  Serial.begin(9600);
  Serial.println("Send 2 pieces of data - 2 floats - structure: <9.99|9.99>");
  Serial.println();
}//End setup

//====================

void loop(){
  receiveData();

  if (newData == true){
    parseData();
    Serial.println(receivedChars);
    Serial.println(altFromPC);
    Serial.println(azFromPC);
    Serial.println();
    newData = false;
  }//End if
}//End loop

//====================

void receiveData(){
  static boolean recvInProgress = false;    //Komt er nog data binnen?
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
        receivedChars[i] = '\0';           //Eindig de string met NULL
        recvInProgress = false;
        i = 0;
        newData = true;
      }//End if else
    }//End if / else if
  }//End while loop
}//End receiveData

//====================

void parseData(){
  char * strtokIndex;                               //strtok() gebruikt dit als index

  strcpy(tempChars, receivedChars);                 //Copieer receivedChars naar tempChars

  strtokIndex = strtok(tempChars, sectionMarker);   //Neem 1ste deel van de data
  altFromPC = atol(strtokIndex);                    //Sla het op in altFromPC

  strtokIndex = strtok(NULL, sectionMarker);        //Doet voort waar hij gestopt was
  azFromPC = atol(strtokIndex);                     //Sla het op in azFromPC
}//End parseData
