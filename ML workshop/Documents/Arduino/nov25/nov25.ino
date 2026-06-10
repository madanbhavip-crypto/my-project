/* ============================================================
   LINE FOLLOWING BOT - ATMEGA2560 (ARDUINO MEGA)
   3 IR SENSORS (A0, A1, A2)
   MOTOR DRIVER: L298N
   PID CONTROL IMPLEMENTED
   ============================================================ */

//// -------- Pin Definitions -------- ////

// IR Sensors
#define IR_LEFT   A0
#define IR_CENTER A1
#define IR_RIGHT  A2

// L298N Motor Driver Pins
#define ENA 5     // Left motor PWM
#define IN1 22
#define IN2 23
#define IN3 24
#define IN4 25
#define ENB 6     // Right motor PWM

//// -------- PID Variables -------- ////
float Kp = 25.0;
float Ki = 0.0;
float Kd = 12.0;

float error = 0, previous_error = 0;
float integral = 0, derivative = 0;
int PID_value = 0;

//// -------- Robot Speed -------- ////
int baseSpeed = 140;    // 0–255
int maxSpeed = 255;

//// -------- Functions -------- ////

void leftMotor(int speed) {
  if (speed > 0) {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    analogWrite(ENA, speed);
  } else {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    analogWrite(ENA, -speed);
  }
}

void rightMotor(int speed) {
  if (speed > 0) {
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
    analogWrite(ENB, speed);
  } else {
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
    analogWrite(ENB, -speed);
  }
}

//// -------- Setup -------- ////
void setup() {
  pinMode(IR_LEFT, INPUT);
  pinMode(IR_CENTER, INPUT);
  pinMode(IR_RIGHT, INPUT);

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);

  Serial.begin(9600);
}

//// -------- Main Loop -------- ////
void loop() {

  // Read sensors (active LOW)
  int L = analogRead(IR_LEFT);
  int C = analogRead(IR_CENTER);
  int R = analogRead(IR_RIGHT);

  // Threshold for line detection
  int threshold = 600; // adjust according to your sensor

  // Convert sensor values to digital-like 0/1
  int left  = (L < threshold) ? 1 : 0;
  int center = (C < threshold) ? 1 : 0;
  int right = (R < threshold) ? 1 : 0;

  // ------- POSITION ERROR CALCULATION -------
  if (left && !center && !right)      error = -2;   // line on left
  else if (left && center && !right)  error = -1;
  else if (!left && center && !right) error = 0;    // perfect center
  else if (!left && center && right)  error = 1;
  else if (!left && !center && right) error = 2;    // line on right
  else if (!left && !center && !right) error = previous_error; // lost line (use old error)

  // ------- PID CALCULATION -------
  integral += error;
  derivative = error - previous_error;

  PID_value = (Kp * error) + (Ki * integral) + (Kd * derivative);

  previous_error = error;

  // ------- MOTOR SPEED CONTROL -------
  int leftSpeed  = baseSpeed + PID_value;
  int rightSpeed = baseSpeed - PID_value;

  // speed limits
  leftSpeed  = constrain(leftSpeed, -maxSpeed, maxSpeed);
  rightSpeed = constrain(rightSpeed, -maxSpeed, maxSpeed);

  // write to motors
  leftMotor(leftSpeed);
  rightMotor(rightSpeed);

  // debugging info (optional)
  // Serial.print("Err: "); Serial.print(error);
  // Serial.print(" PID: "); Serial.println(PID_value);
}
