/*
 * IR AC Receiver - dump raw IR signals serial port
 * An PhotoTransistor must be connected to Arduino pin 11.
 * Version 1.0 September 2013
 * Copyright 2013 Itamar Ostricher
 * http://itamaro.com/ , https://github.com/itamaro/home-control-arduino
 * Shamelessly based on the IRrecvDump example from the IRremote library
 * (https://github.com/shirriff/Arduino-IRremote/blob/master/examples/IRrecvDump/IRrecvDump.ino)
 */

#include <IRremote.h>

#define RECV_PIN 11

IRrecv irrecv(RECV_PIN);

decode_results results;

void setup()
{
  Serial.begin(9600);
  irrecv.enableIRIn(); // Start the receiver
}

// Dumps out the decode_results raw data.
// Call this after IRrecv::decode()
void dump(decode_results *results)
{
  Serial.print("0x");
  Serial.print(results->value, HEX);
  Serial.print(" (");
  Serial.print(results->bits, DEC);
  Serial.println(" bits)");
  Serial.print("Raw (");
  Serial.print(results->rawlen, DEC);
  Serial.print("):");
  for (int i=0; i < results->rawlen; ++i)
  {
    Serial.print(" ");
    if ((i % 2) == 0)
	{
	  // Mark gaps (spaces) as negative numbers in the output
      Serial.print("-");
    }
	// Display mark/space lengths in microseconds
    Serial.print(results->rawbuf[i]*USECPERTICK, DEC);
  }
  Serial.println("");
}

void loop()
{
  if (irrecv.decode(&results))
  {
    Serial.println(results.value, HEX);
    dump(&results);
    irrecv.resume(); // Receive the next value
  }
}
