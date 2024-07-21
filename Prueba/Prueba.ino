#include <Servo.h>

Servo myServo;
float currentX = 0;
float currentY = 0;
float volume = 0;
float timeRequired = 0;

void setup() {
  Serial.begin(9600);
  myServo.attach(9);  // Pin al que está conectado el servo
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    if (command.startsWith("MOVE")) {
      handleMoveCommand(command);
    } else if (command.startsWith("CALIBRATE")) {
      handleCalibrateCommand();
    } else if (command.startsWith("SET VOLUME")) {
      handleSetVolumeCommand(command);
    } else if (command.startsWith("SET TIME")) {
      handleSetTimeCommand(command);
    }
  }
}

void handleMoveCommand(String command) {
  int indexX = command.indexOf('X');
  int indexY = command.indexOf('Y');
  if (indexX != -1) {
    float valueX = command.substring(indexX + 2).toFloat();  // Extracción del valor de X
    currentX += valueX;
  }
  if (indexY != -1) {
    float valueY = command.substring(indexY + 2).toFloat();  // Extracción del valor de Y
    currentY += valueY;
  }
  Serial.print("X: ");
  Serial.print(currentX);
  Serial.print(", Y: ");
  Serial.print(currentY);
  Serial.print(", Z: ");
  Serial.println(myServo.read());  // Asumiendo que Z está controlado por un servo
}

void handleCalibrateCommand() {
  currentX = 0;
  currentY = 0;
  myServo.write(0);  // Calibrar servo en la posición 0
  Serial.println("Calibración completa");
}

void handleSetVolumeCommand(String command) {
  int index = command.indexOf(' ') + 1;
  volume = command.substring(index).toFloat();
  Serial.print("Volumen establecido a: ");
  Serial.println(volume);
}

void handleSetTimeCommand(String command) {
  int index = command.indexOf(' ') + 1;
  timeRequired = command.substring(index).toFloat();
  Serial.print("Tiempo establecido a: ");
  Serial.println(timeRequired);
}
