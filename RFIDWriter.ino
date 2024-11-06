#include <Wire.h>
#include <MFRC522_I2C.h>  // Correct library

#define I2C_ADDRESS 0x28
MFRC522_I2C mfrc522(I2C_ADDRESS, 0, &Wire); // Initialize with address and Wire instance

String dataToWrite = ""; // Stores binary data from GUI
bool readyToWrite = false; // Flag to trigger write after data received

void sendToGui(const char* message) {
  Serial.print("Diagnostic: ");
  Serial.println(message);
}

void setup() {
  Serial.begin(115200);
  Wire.begin(); 
  mfrc522.PCD_Init(); 
  sendToGui("RFID module initialized. Ready for commands.");
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');

    if (command.startsWith("write")) {
      dataToWrite = command.substring(6);
      readyToWrite = true;
      sendToGui("Data received and stored. Ready to write.");
    } 
    else if (command.startsWith("read")) {
      readRFID();
    }
    else if (command.startsWith("clear")) {
      clearBlock(4); // Clear block 4 only when "clear" command is received
    }
  }

  if (readyToWrite) {
    delay(500);  // Delay to allow tag stabilization
    writeRFID();
    readyToWrite = false;
  }
}

// Function to clear the block by writing zeroes
void clearBlock(byte blockAddr) {
  byte zeroBuffer[16] = {0}; // 16 bytes of zero
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    sendToGui("Attempting to clear data block with zeroes.");
    MFRC522_I2C::StatusCode status = mfrc522.MIFARE_Write(blockAddr, zeroBuffer, 16);
    
    if (status == MFRC522_I2C::STATUS_OK) {
      Serial.print("Diagnostic: Cleared data block with zeroes: ");
      for (int i = 0; i < 16; i++) {
        Serial.print(zeroBuffer[i], HEX);
        Serial.print(" ");
      }
      Serial.println();
      sendToGui("Cleared data block with zeroes.");
    } else {
      sendToGui("Failed to clear data block.");
    }
    mfrc522.PICC_HaltA();
  } else {
    sendToGui("Failed to detect RFID tag for clearing.");
  }
}

void writeRFID() {
  if (dataToWrite.length() != 56) { // Each hex byte is 8 bits, 7 bytes -> 56 bits
    sendToGui("Invalid data length.");
    return;
  }

  byte buffer[16] = {0}; // Initialize 16-byte buffer with zeros

  // Convert binary string to byte array
  for (int i = 0; i < 7; i++) {
    String byteString = dataToWrite.substring(i * 8, (i + 1) * 8);
    buffer[i] = strtol(byteString.c_str(), NULL, 2);
  }

  sendToGui("Attempting to write data:");
  Serial.print("Diagnostic: Writing data: ");
  for (int i = 0; i < 16; i++) {
    Serial.print(buffer[i], HEX);
    Serial.print(" ");
  }
  Serial.println();

  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    MFRC522_I2C::StatusCode status = mfrc522.MIFARE_Write(4, buffer, 16);
    if (status == MFRC522_I2C::STATUS_OK) {
      sendToGui("Data written successfully.");
    } else {
      sendToGui("Failed to write data.");
    }
    mfrc522.PICC_HaltA();
  } else {
    sendToGui("Failed to detect RFID tag.");
  }
}

void readRFID() {
  byte buffer[18];
  byte size = sizeof(buffer);

  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    MFRC522_I2C::StatusCode status = mfrc522.MIFARE_Read(4, buffer, &size);
    if (status == MFRC522_I2C::STATUS_OK) {
      Serial.print("Data: ");
      for (byte i = 0; i < 7; i++) {
        // Ensure each byte is displayed as two hex digits, adding a leading zero if needed
        if (buffer[i] < 0x10) Serial.print("0");
        Serial.print(buffer[i], HEX);
        Serial.print(" ");
      }
      Serial.println();
    } else {
      sendToGui("Failed to read data.");
    }
    mfrc522.PICC_HaltA();
  } else {
    sendToGui("No RFID tag found.");
  }
}
