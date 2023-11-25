#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <FirebaseArduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <Servo.h>
#define FIREBASE_HOST "iotnhom7-c18f8-default-rtdb.asia-southeast1.firebasedatabase.app"
#define FIREBASE_AUTH "c8iuszd9hKUIHa1FrWQCZq2I8dsOMvVwaymx8Ilz"

const char* ssid = "Room cho nguoi huong noi";
const char* password = "123456789";
const char* empty = "Empt";
const char* fill = "fill";
const int ir_1 = D5;
const int ir_2 = D6;
const int ir_3 = D7;
const int servo_in_pin = D3;
const int servo_out_pin = D4;

int previousMillis = 0;
const long interval = 5000;
int total = 3, remain = 3, s1 = 0, s2 = 0, s3 = 0;
ESP8266WebServer server(80);
Servo servo_in, servo_out;
LiquidCrystal_I2C lcd(0x27, 16, 2);  // Set the LCD address to 0x27 for a 16 chars and 2 line display

void initServo() {
  servo_in.attach(servo_in_pin);
  servo_out.attach(servo_out_pin);
  servo_in.write(0);
  servo_out.write(0);
}

void initSensors() {
  pinMode(ir_1, INPUT);
  pinMode(ir_2, INPUT);
  pinMode(ir_3, INPUT);
}
void displayMessage(const char* s, int duration) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(s);
  if (duration != -1)
    delay(duration);
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
  displayMessage("Connecting...", -1);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print("..");
  }
  Serial.println("Nodemcu(esp8266) is connected to the ssid");
  Serial.println(WiFi.localIP());
  
  server.on("/", HTTP_GET, handleRoot);
  server.on("/entrance", HTTP_GET, handleEntrance);
  server.on("/exit", HTTP_GET, handleExit);
  server.begin();
  displayMessage("Connected wifi", -1);
  delay(1000);
  lcd.clear();
}

void handleRoot() {
}

// http://<IP>/entrance?state=open&mode=0&message=allow
void handleEntrance() {
  Serial.println("Entrance Request Received!");
  String state = server.arg("state");
  String mode = server.arg("mode");
  String message = server.arg("message");
  Serial.println(remain);
  if (message == "allow") {   // cho phép vào
    if (mode == "1") {        // Tự động
      if (state == "open") {  // yêu cầu mở cổng
        if (remain > 0) {    // còn slot
          servo_in.write(90);
          server.send(200, "text/plain", "Open entrance successfully, slot - 1 " + remain);
        } else {  // hết slot
          displayMessage("Out of slot", 5000);
          server.send(200, "text/plain", "Out of slot");
        }
      } else {  // yêu cầu đóng cổng
        servo_in.write(0);
        remain -= 1;
        server.send(200, "text/plain", "Close entrance successfully, " + remain);
      }
    } else {  // con người điều khiển
      if (state == "open") {
        servo_in.write(90);
        server.send(200, "text/plain", "Open entrance successfully, remain slot " + remain);
      } else {
        servo_in.write(0);
        server.send(200, "text/plain", "Close entrance successfully");
      }
    }
  } else {  // không cho phép vào
    displayMessage(message.c_str(), 5000);
    server.send(200, "text/plain", message.c_str());
  }
}
// http://<IP>/exit?state=open&mode=0
void handleExit() {
  Serial.println("Exit request received!");
  String state = server.arg("state");
  String mode = server.arg("mode");
  if (mode == "1") {        // Tự động
    if (state == "open") {  // yêu cầu mở cổng
      servo_out.write(90);
      server.send(200, "text/plain", "Open exit successfully " + remain);
    } else {  // yêu cầu đóng cổng
      servo_out.write(0);
      remain += 1;
      server.send(200, "text/plain", "close exit successfully, slot + 1 " + remain);
    }
  } else {  // con người điều khiển
    if (state == "open") {
      servo_out.write(90);
      server.send(200, "text/plain", "Open exit successfully, remain slot " + remain);
    } else {
      servo_out.write(0);
      server.send(200, "text/plain", "Close exit successfully, remain slot " + remain);
    }
  }
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
  lcd.clear();
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
  Firebase.setInt("Parking/Slot1", s1);
  Firebase.setInt("Parking/Slot2", s2);
  Firebase.setInt("Parking/Slot3", s3);
  if (Firebase.failed()) {

    //Serial.print("pushing /logs failed:");
    Serial.println(Firebase.error());
    return;
  }
}
void loop() {
  server.handleClient();
  long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    updateLCD();
    pushToFirebase();
    yield();
  }
}