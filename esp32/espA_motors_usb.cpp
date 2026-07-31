#include <Arduino.h>

/* ===================== MOTOR PINS (unchanged from espA_motors_encoders.cpp) ===================== */
// Local ID 0: Gripper
#define M0_DIR 32
#define M0_PWM 33

// Local ID 1: Wrist1
#define M1_DIR 27
#define M1_PWM 14

// Local ID 2: Wrist2
#define M2_DIR 22
#define M2_PWM 23

struct MotorPin {
  int dir;
  int pwm;
};

MotorPin motorPins[3] = {
  {M0_DIR, M0_PWM},
  {M1_DIR, M1_PWM},
  {M2_DIR, M2_PWM}
};

void setMotor(uint8_t id, bool fwd, uint8_t pwm) {
  if (id > 2) return;
  digitalWrite(motorPins[id].dir, fwd ? HIGH : LOW);
  analogWrite(motorPins[id].pwm, pwm);
}

/* ===================== SETUP ===================== */
void setup() {
  // Same baud the writer node expects. This is now the ONLY link (USB),
  // no BluetoothSerial, so it's the one thing that must match on both ends.
  Serial.begin(115200);

  for (int i = 0; i < 3; i++) {
    pinMode(motorPins[i].dir, OUTPUT);
    pinMode(motorPins[i].pwm, OUTPUT);
    digitalWrite(motorPins[i].dir, LOW);
    analogWrite(motorPins[i].pwm, 0);
  }

  Serial.println("ESP-A (USB, motors only) ready");
}

/* ===================== LOOP ===================== */
void loop() {
  // Same 3-byte packet format as the BT version: [local_id, direction(0/1), pwm].
  // No 0xFF homing sentinel here — homing needs limit switches, which this
  // stripped build doesn't wire up. If id==0xFF ever arrives, it's > 2 and
  // setMotor() just ignores it, so it's harmless.
  while (Serial.available() >= 3) {
    uint8_t id  = Serial.read();
    uint8_t dir = Serial.read();
    uint8_t pwm = Serial.read();
    setMotor(id, dir, pwm);
  }
}
