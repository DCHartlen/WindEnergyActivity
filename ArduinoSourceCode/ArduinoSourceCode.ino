/*
 *  Wind Turbine Activity Data Aquisition System
 *  Uses an Adafruit Itsy Bitys to record voltage from 
 *  a DC motor driven by the wind turbine, displays
 *  voltage to an LCD screen using I2C, and outputs all
 *  voltage data to serial.
 *  
 *  Created By:    Devon C. Hartlen, EIT
 *  Date:          13-Jun-2018
 *  Modified By:   
 *  Date:          
*/

// include the library code:
#include "Wire.h"
#include "Adafruit_LiquidCrystal.h"

// Initalize LCD screen through I2C, Address #0
Adafruit_LiquidCrystal lcd(0);

// Generator voltage pin
const int pinGenerator = A5;

// Define refresh frequencies. Units of hertz (1/s)
int samplingFreq = 100;   // How often data is read from pin
int displayFreq = 5;      // How often LCD screen is updated

// Define millisecond counters for interrupt based sampling
unsigned long currentMillis = 0;
unsigned long lastSampleMillis = 0;
unsigned long lastDisplayMillis = 0;

// Initialize voltage variables
int vNew = 0;   // newly read voltage (bits)
int vOld = 0;   // previous voltage used for filtering (bits)
float vAct = 0.0;  // actual voltage converted to volts
float alpha = 0.995; // Low pass filter constant
float b2v = 3.3/1024.0; // bits (arduino native 2^10 bits) to volts (V/bit)

// This section contains initialization codes
void setup() {
  // Initialize LCD screen size (uses 16x2 display)
  lcd.begin(16,2);
  // Print Initialization message
  lcd.setBacklight(HIGH);
  lcd.setCursor(3,0);
  lcd.print("Loading...");

  // Set up serial communication
  Serial.begin(9600);

  // Convert both frequencies to millis
  samplingFreq = 1000/samplingFreq;
  displayFreq = 1000/displayFreq;

  // Delay for suspense
  delay(3000);

  // Set  row of LCD to display "VOLTAGE"
  lcd.clear();
  lcd.setCursor(4,0);
  lcd.print("VOLTAGE:");
}  // end void setup


// put your main code here, to run repeatedly:
void loop() {
  currentMillis = millis();
  
  // Check interrupt for sampling and send over serial. 
  if ((currentMillis - lastSampleMillis) > samplingFreq) {
    // Read voltage (bits) from analog pin
    vNew = analogRead(pinGenerator);
    // Two things here. 1) running first order low pass filter on raw 
    // input (in bits), 2) converting bits to volts.
    vAct = (alpha*float(vOld) + (1.0-alpha)*float(vNew))*b2v;
    //Saving old voltage for next iteration (in bits)
    vOld = vNew;
    // print the actual voltage to serial
    Serial.println(vAct);
    // Update lastSampleMillis to trigger next iterupt
    lastSampleMillis = currentMillis;
  } // end interrupt for serial print

  // Check interrupt for lcd display update. No math here, all done above.
  if ((currentMillis-lastDisplayMillis) > displayFreq) {
    // Set the cursor each time or LCD will print forever
    lcd.setCursor(5,1);
    // Print actual voltage (float) to screen
    lcd.print(vAct);
    // enforce a space before putting tacking on units
    lcd.setCursor(9,1);
    lcd.print(" V");
    // Update lastDisplayMillis to trigger next iterrupt
    lastDisplayMillis = currentMillis;
  } // end interrupt for lcd display

}
