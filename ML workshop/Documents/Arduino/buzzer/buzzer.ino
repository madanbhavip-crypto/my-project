int buzzerPin = 8;
void setup() {
  pinMode(buzzerPin, OUTPUT);// put your setup code here, to run once:

}

void loop() {
  digitalWrite(buzzerPin, HIGH);
  delay(1000);
  digitalWrite(buzzerPin, LOW);
  delay(500);
  digitalWrite(buzzerPin, HIGH);
  delay(5000);
  digitalWrite(buzzerPin, LOW);
  delay(500);

  // put your main code here, to run repeatedly:

}
