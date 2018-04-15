#include <FUTABA_SBUS.h>
#include <Servo.h> 
#include <SoftwareSerial.h>

SoftwareSerial mserial(10, 11); // RX, TX
FUTABA_SBUS sBus;

void setup(){
  mserial.begin(57600);
  sBus.begin();
}

void loop(){

  //delay(25);
  sBus.FeedLine();
  if (sBus.toChannels == 1){
    //sBus.UpdateServos();
    sBus.UpdateChannels();
    sBus.toChannels = 0;

    mserial.print(sBus.channels[0]);
    mserial.print("\t");    
    mserial.print(sBus.channels[1]);
    mserial.print("\t");
    mserial.print(sBus.channels[2]);
    mserial.print("\t");
    mserial.print(sBus.channels[3]);
    mserial.print("\t");
    mserial.print(sBus.channels[4]);
    mserial.print("\t");
    mserial.print(sBus.channels[5]);
    mserial.print("\t");
    mserial.print(sBus.channels[6]);
    mserial.print("\t");
    
    mserial.print(sBus.channels[7]);
    mserial.print("\t");
    mserial.print(sBus.channels[8]);
    mserial.print("\t");
    mserial.print(sBus.channels[9]);
    mserial.print("\t");
    mserial.print(sBus.channels[10]);
    mserial.print("\t");
    mserial.print(sBus.channels[11]);
    mserial.print("\t");

    mserial.print(sBus.channels[12]);
    mserial.print("\t");
    mserial.print(sBus.channels[13]);
    mserial.print("\t");
    mserial.print(sBus.channels[14]);
    mserial.print("\t");
    mserial.println(sBus.channels[15]);
    //mserial.println("Test test test 123 test test test test");
  }
}

