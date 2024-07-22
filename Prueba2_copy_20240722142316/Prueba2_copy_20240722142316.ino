#include <Arduino.h>

float x_pos = 0.0;
float y_pos = 0.0;
float z_pos = 0.0;

void setup() {
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    processCommand(command);
  }
  Serial.print("X:");
  Serial.print(x_pos);
  Serial.print(",Y:");
  Serial.print(y_pos);
  Serial.print(",Z:");
  Serial.println(z_pos);
  
  delay(1000);
}

void processCommand(String command) {
  if (command.startsWith("X")) {
    x_pos = command.substring(2).toFloat();
  } 
  else if (command.startsWith("Y")) {
    y_pos = command.substring(2).toFloat();
  } 
  else if (command.startsWith("Z")) {
    z_pos = command.substring(2).toFloat();
  } 
  else if (command.startsWith("CALIBRAR")) {
  } 
  else if (command.startsWith("SET_PARAMS")) {
  }
}
