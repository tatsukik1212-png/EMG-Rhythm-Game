// =====================
// CHEST EMG
// =====================

const int LEFT_CHEST_PIN  = A0;
const int RIGHT_CHEST_PIN = A1;

void setup() {
    Serial.begin(115200);

    pinMode(LEFT_CHEST_PIN, INPUT);
    pinMode(RIGHT_CHEST_PIN, INPUT);
}

void loop() {

    int left_chest  = analogRead(LEFT_CHEST_PIN);
    int right_chest = analogRead(RIGHT_CHEST_PIN);

    Serial.print(left_chest);
    Serial.print(",");

    Serial.println(right_chest);

    delay(10);
}
// =====================
// ARM EMG
// =====================

const int LEFT_ARM_PIN  = A0;
const int RIGHT_ARM_PIN = A1;

void setup() {

    Serial.begin(115200);

    pinMode(LEFT_ARM_PIN, INPUT);
    pinMode(RIGHT_ARM_PIN, INPUT);
}

void loop() {

    int left_arm  = analogRead(LEFT_ARM_PIN);
    int right_arm = analogRead(RIGHT_ARM_PIN);

    Serial.print(left_arm);
    Serial.print(",");

    Serial.println(right_arm);

    delay(10);
}