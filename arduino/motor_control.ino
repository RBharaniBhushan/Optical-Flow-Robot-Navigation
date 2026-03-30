/*
 * Motor Control for Autonomous Navigation
 * Receives commands from Raspberry Pi via USB Serial
 * Author: R Bharani Bhushan
 */

// ─────────────────────────────────────
// MOTOR PINS (L298N)
// ─────────────────────────────────────
#define ENA 11  // Left speed PWM
#define IN1 10  // Left forward
#define IN2 9   // Left backward
#define IN3 8   // Right forward
#define IN4 7   // Right backward
#define ENB 6   // Right speed PWM

int spd = 150;  // Default speed (0-255)

void setup() {
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENB, OUTPUT);
  stopMotors();
  Serial.begin(9600);
  delay(1000);
  Serial.println("READY");
}

void loop() {
  if (Serial.available() > 0) {
    String cmd = "";
    while (Serial.available() > 0) {
      char c = Serial.read();
      if (c != '\n' && c != '\r') {
        cmd += c;
      }
    }
    delay(10);

    if (cmd == "F") {
      moveForward();
      Serial.println("OK:FORWARD");
    }
    else if (cmd == "B") {
      moveBackward();
      Serial.println("OK:BACKWARD");
    }
    else if (cmd == "L") {
      turnLeft();
      Serial.println("OK:LEFT");
    }
    else if (cmd == "R") {
      turnRight();
      Serial.println("OK:RIGHT");
    }
    else if (cmd == "S") {
      stopMotors();
      Serial.println("OK:STOP");
    }
    else if (cmd == "READY") {
      Serial.println("OK:READY");
    }
    else if (cmd.startsWith("SPD")) {
      spd = constrain(cmd.substring(3).toInt(), 0, 255);
      Serial.print("OK:SPD:");
      Serial.println(spd);
    }
    else if (cmd.startsWith("TL")) {
      int deg = cmd.substring(2).toInt();
      turnLeftDeg(deg);
      Serial.println("OK:TL");
    }
    else if (cmd.startsWith("TR")) {
      int deg = cmd.substring(2).toInt();
      turnRightDeg(deg);
      Serial.println("OK:TR");
    }
    else if (cmd.startsWith("MF")) {
      int ms = cmd.substring(2).toInt();
      moveForwardTime(ms);
      Serial.println("OK:MF");
    }
    else if (cmd.length() > 0) {
      Serial.println("ERR:UNKNOWN");
    }
  }
}

void moveForward() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  analogWrite(ENA, spd);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  analogWrite(ENB, spd);
}

void moveBackward() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  analogWrite(ENA, spd);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  analogWrite(ENB, spd);
}

void turnLeft() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  analogWrite(ENA, spd);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  analogWrite(ENB, spd);
}

void turnRight() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  analogWrite(ENA, spd);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  analogWrite(ENB, spd);
}

void stopMotors() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  analogWrite(ENA, 0);
  analogWrite(ENB, 0);
}

void moveForwardTime(int ms) {
  moveForward();
  delay(ms);
  stopMotors();
}

void turnLeftDeg(int deg) {
  int turnTime = deg * 8;
  turnLeft();
  delay(turnTime);
  stopMotors();
}

void turnRightDeg(int deg) {
  int turnTime = deg * 8;
  turnRight();
  delay(turnTime);
  stopMotors();
}
