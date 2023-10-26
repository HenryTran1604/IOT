#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <FirebaseArduino.h> 
#include <ESP8266WiFi.h>
#include <Servo.h>
#define FIREBASE_HOST "iotn7-e47bc-default-rtdb.firebaseio.com"
#define FIREBASE_AUTH "QPRjTyKXsSK5DWVIyboqFNkBNoR0lPYQajmxnSMn"

const char* ssid = "TQH";
const char* password = "123456789";
const char* empty = "Empt";
const char* fill = "fill";
const int ir_1 = D3;
const int ir_2 = D7;
const int ir_3 = D5;
const int servo_pin = D6;
int counter = 0;
int total = 3, remain, s1 = 0, s2 = 0, s3 = 0;
WiFiServer server(80);
Servo servo;
LiquidCrystal_I2C lcd(0x27, 16, 2);  // Set the LCD address to 0x27 for a 16 chars and 2 line display

void initServo() {
  servo.attach(servo_pin);
}

void initSensors() {
  pinMode(ir_1, INPUT);
  pinMode(ir_2, INPUT);
  pinMode(ir_3, INPUT);
}

void initLCD() {
  lcd.begin();      // Initialize the LCD
  lcd.backlight();  // Turn on the backlight
  lcd.clear();      // Clear the LCD screen
  lcd.setCursor(0, 0);
  lcd.print(" Car  parking  ");
  lcd.setCursor(0, 1);
  lcd.print("    System     ");
  delay(2000);
  lcd.clear();
}
void initWifi() {
  Serial.print("Connecting to.");
  Serial.println(ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print("..");
  }
  Serial.println("Nodemcu(esp8266) is connected to the ssid");
  Serial.println(WiFi.localIP());
  server.begin();
  delay(1000);
}
void openEntranceBarrier() {
  servo.write(180);
}
void closeEntranceBarrier() {
  servo.write(0);
}
void controlBarrier() {
  // put your main code here, to run repeatedly:
  WiFiClient client;
  client = server.available();

  if (client == 1) {
    String request = client.readStringUntil('\n');
    client.flush();
    Serial.println(request);
    if (request.indexOf("openentrancebarrier") != -1) {
      openEntranceBarrier();
      Serial.println("Entrance barrier is opening now");
    } else if (request.indexOf("closeentrancebarrier") != -1) {
      closeEntranceBarrier();
      Serial.println("LED IS OFF NOW");
    }
    client.println("HTTP/1.1 200 OK");
    Serial.print("Client Disconnected");
    Serial.println("===========================================================");
    Serial.println("                              ");
  }
}
void updateToFirebase() {
}
void readSensors() {
  s1 = 0, s2 = 0, s3 = 0;

  if (digitalRead(ir_1) == 0) {
    s1 = 1;
  }
  if (digitalRead(ir_2) == 0) {
    s2 = 1;
  }
  if (digitalRead(ir_3) == 0) {
    s3 = 1;
  }
}
void setup() {
  Serial.begin(9600);
  initServo();
  initSensors();
  initLCD();
  initWifi();
  Firebase.begin(FIREBASE_HOST, FIREBASE_AUTH);
}

void updateLCD() {
  readSensors();
  lcd.setCursor(0, 0);  // Set the cursor to the first column and first row
  if (s1 == 1) {
    lcd.print("S1:Fill ");
  } else {
    lcd.print("S1:Empt");
  }
  lcd.setCursor(9, 0);
  if (s2 == 1) {
    lcd.print("S2:Fill ");
  } else {
    lcd.print("S2:Empt");
  }

  lcd.setCursor(4, 1);
  if (s3 == 1) {
    lcd.print("S3:Fill ");
  } else {
    lcd.print("S3:Empty");
  }
}
void pushToFirebase() {
  Firebase.setInt("slot1", s1);   
  Firebase.setInt("slot2", s2);  
  Firebase.setInt("slot3", s3);
  if (Firebase.failed()) {

    //Serial.print("pushing /logs failed:");
    Serial.println(Firebase.error());
    return;
  }
}
void loop() {
  updateLCD();
  controlBarrier();
  pushToFirebase();
}