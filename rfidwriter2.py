import sys
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QTextEdit, QMessageBox
)
from PyQt5.QtCore import QTimer

class RFID_GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.serial_port = None

    def initUI(self):
        # Connect/Disconnect Button and Status
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.toggle_connection)
        self.status_label = QLabel("Status: Disconnected")

        # Read, Write, and Clear Buttons
        self.read_button = QPushButton("Read")
        self.read_button.clicked.connect(self.read_rfid)
        self.read_button.setEnabled(False)
        
        self.write_button = QPushButton("Write")
        self.write_button.clicked.connect(self.write_rfid)
        self.write_button.setEnabled(False)

        self.clear_button = QPushButton("Zeroise")  # New Clear button
        self.clear_button.clicked.connect(self.clear_rfid)
        self.clear_button.setEnabled(False)

        # Hex Code Input
        self.hex_input = QLineEdit()
        self.hex_input.setPlaceholderText("Enter 7 two-digit hex codes (e.g., 12 AB CD 34 EF 56 78)")

        # Log Box for Serial Monitor
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)

        # Layout Setup
        layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.connect_button)
        top_layout.addWidget(self.status_label)
        layout.addLayout(top_layout)

        layout.addWidget(self.hex_input)
        layout.addWidget(self.write_button)
        layout.addWidget(self.read_button)
        layout.addWidget(self.clear_button)  # Add Clear button to layout
        layout.addWidget(QLabel("Log:"))
        layout.addWidget(self.log_box)

        self.setLayout(layout)
        self.setWindowTitle("RFID Controller")

        # Timer to poll serial data
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_serial_data)

    def toggle_connection(self):
        if self.serial_port and self.serial_port.is_open:
            self.disconnect_serial()
        else:
            self.connect_serial()

    def connect_serial(self):
        ports = serial.tools.list_ports.comports()
        port_name = None
        for port in ports:
            if 'Nano' in port.description or 'USB' in port.description:
                port_name = port.device
                break

        if not port_name:
            QMessageBox.critical(self, "Error", "Arduino not found.")
            return

        try:
            self.serial_port = serial.Serial(port_name, 115200)
            self.status_label.setText("Status: Connected")
            self.connect_button.setText("Disconnect")
            self.read_button.setEnabled(True)
            self.write_button.setEnabled(True)
            self.clear_button.setEnabled(True)  # Enable Clear button
            self.timer.start(100)  # Poll serial every 100ms
            self.log_box.append("Connected to Arduino")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to connect: {e}")

    def disconnect_serial(self):
        if self.serial_port:
            self.serial_port.close()
        self.status_label.setText("Status: Disconnected")
        self.connect_button.setText("Connect")
        self.read_button.setEnabled(False)
        self.write_button.setEnabled(False)
        self.clear_button.setEnabled(False)  # Disable Clear button
        self.timer.stop()
        self.log_box.append("Disconnected from Arduino")

    def write_rfid(self):
        hex_values = self.hex_input.text().split()
        if len(hex_values) != 7 or not all(len(x) == 2 and all(c in '0123456789ABCDEFabcdef' for c in x) for x in hex_values):
            QMessageBox.warning(self, "Input Error", "Enter 7 two-digit hex codes.")
            return

        # Convert hex values to binary string
        binary_data = ''.join(format(int(x, 16), '08b') for x in hex_values)
        command = f"write {binary_data}\n"
        self.send_command(command)

    def clear_rfid(self):
        command = "clear\n"
        self.send_command(command)

    def read_rfid(self):
        command = "read\n"
        self.send_command(command)

    def send_command(self, command):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write(command.encode())
            self.log_box.append(f"Sent: {command.strip()}")

    def read_serial_data(self):
        if self.serial_port and self.serial_port.in_waiting > 0:
            data = self.serial_port.readline().decode().strip()
            if data.startswith("Diagnostic:"):
                self.log_box.append(data)  # Display diagnostic messages
            else:
                self.log_box.append(f"Received: {data}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = RFID_GUI()
    gui.show()
    sys.exit(app.exec_())
