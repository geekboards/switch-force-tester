/*
   Simple demo, should work with any driver board

   Connect STEP, DIR as indicated

   Copyright (C)2015-2017 Laurentiu Badea

   This file may be redistributed under the terms of the MIT license.
   A copy of this license has been included with this distribution in the file LICENSE.
*/
#include <Arduino.h>
#include "BasicStepperDriver.h"
#include "HX711.h"

// Motor steps per revolution. Most steppers are 200 steps or 1.8 degrees/step
#define MOTOR_STEPS 40
#define RPM 600
#define STEPS_PER_MM 640
// Since microstepping is set externally, make sure this matches the selected mode
// If it doesn't, the motor will move at a different RPM than chosen
// 1=full step, 2=half step etc.
#define MICROSTEPS 8
// All the wires needed for full functionality
#define DIR 2
#define STEP 5
//Uncomment line to use enable/disable functionality
//#define SLEEP 13

HX711 scale;
uint8_t dataPin = A4;
uint8_t clockPin = A5;
uint32_t start, stop;
volatile float f;

uint8_t switchPin = 11;
bool pressed = 0;
bool released = 0;

// 2-wire basic config, microstepping is hardwired on the driver
BasicStepperDriver stepper(MOTOR_STEPS, DIR, STEP);

//Uncomment line to use enable/disable functionality
//BasicStepperDriver stepper(MOTOR_STEPS, DIR, STEP, SLEEP);

void setup() {
  Serial.begin(115200);
  scale.begin(dataPin, clockPin);
  scale.set_scale(7055);
  // reset the scale to zero = 0
  scale.tare();
  pinMode(switchPin, INPUT_PULLUP);
  stepper.begin(RPM, MICROSTEPS);
  //stepper.setSpeedProfile(stepper.LINEAR_SPEED, 1500, 1500);
}

void loop() {
  if (Serial.available())
  {
    char c = Serial.read();
    switch (c)
    {
      case 't': // tare
        scale.tare();
        break;
      case 'z':
        scale.tare();
        f = 0.0;
        while (f < 1.0)
        {
          stepper.move(80);
          f = scale.get_units(1);
        }
        while (f > 0.1)
        {
          stepper.move(-8);
          delay(100);
          f = scale.get_units(4);
        }
        break;
      case 'w': // weigh
        f = scale.get_units(1);
        Serial.println(f);
        break;
      case 'm': // move
        stepper.move(Serial.parseInt());
        break;
      case 'd': // disable motor
        stepper.disable();
        break;
      case 'p': // plot
        int z = 0;
        f = 0;
        pressed = 0;
        released = 0;

        while (f < 100)
        {
          z += 8;
          stepper.move(8);
          delay(100);
          f = scale.get_units(4);
          Serial.print('d'); Serial.print(z); Serial.print(':'); Serial.println(f);
          if (!pressed && !digitalRead(switchPin))
          {
            pressed = 1;
            Serial.print('P'); Serial.print(z); Serial.print(':'); Serial.println(f);
          }
        }

        delay(500);

        while (f > 0.5)
        {
          z -= 8;
          stepper.move(-8);
          delay(100);
          f = scale.get_units(4);
          Serial.print('u'); Serial.print(z); Serial.print(':'); Serial.println(f);
          if (!released && digitalRead(switchPin))
          {
            released = 1;
            Serial.print('R'); Serial.print(z); Serial.print(':'); Serial.println(f);
          }
        }
        break;
      default:
        Serial.println("Unknown cmd");
        break;
    }
    Serial.println(c);
  }



  //  f = scale.get_units(1);
  //  Serial.println(f);
  //
  //  if (f > 110)
  //  {
  //    stepper.move(-3200);
  //  }
  //  else stepper.move(8);
}
