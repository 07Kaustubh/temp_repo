import json
from PyQt5.QtWidgets import QPushButton, QLabel, QVBoxLayout, QMessageBox, QFrame, QMainWindow
from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea, QWidget, QHBoxLayout
from PyQt5.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QScrollArea, QWidget, QMainWindow
from modules.base_screen import BaseScreen
import os
from modules.serialRead import SerialRead
from modules.tcp import TCP
from PyQt5.QtWidgets import QInputDialog
from modules.communication import SerialThread, TCPthread
from modules.utils import *

TEST_JSON_PATH = "./json/SCAN/test/main.json"  # Path to Test Screen JSON

class TestScreen(QMainWindow):
    """Handles the Test screen functionality with dynamic UI generation."""

    def __init__(self):
        super().__init__()  # No arguments here
        uic.loadUi("./UI/testscreen.ui", self)  # Load UI separately
        self.setWindowTitle("Test Mode")
        self.scroll_area = None
        self.scroll_content = None
        self.main_layout = None

        self.initUI()
        self.load_fields()
        self.__getPortDialoge()

    def initUI(self):
        """Initialize fixed UI components."""
        self.setAutoFillBackground(True)
        self.testbtn = self.findChild(QPushButton, 'testbtn')
        self.testbtn.clicked.connect(self.test)
        self.status_frame = self.findChild(QFrame, 'frame_7')

        # Clear old layout if it exists
        if self.status_frame.layout():
            while self.status_frame.layout().count():
                item = self.status_frame.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            QWidget().setLayout(self.status_frame.layout())

        # Scroll area setup
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background-color: #743d3d; border: none;")

        self.scroll_content = QWidget()
        self.main_layout = QVBoxLayout(self.scroll_content)
        self.main_layout.setSpacing(10)

        # UI Element Storage
        self.test_buttons = {}      # Main test buttons
        self.status_labels = {}     # Main status labels
        self.detail_frames = {}     # Frames to hold detailed subfields
        self.detail_widgets = {}    # Dictionary of dictionaries for subfield widgets
        self.toggle_buttons = {}    # Expand/collapse buttons
        
        self.saved_data = {}
        self.seed="1234"
        self.checksum="4\xd1"

    def load_fields(self):
        """Dynamically load test cases with expandable fields from JSON."""
        try:
            with open(TEST_JSON_PATH, 'r') as file:
                jsndta = json.load(file)

            if jsndta:
                for test in jsndta["Title"]:
                    test_name = test["name"]
                    test_code = test["code"]
                    test_body = test.get("body", [])

                    # Create test row
                    row_frame = QFrame()
                    row_layout = QHBoxLayout(row_frame)
                    row_layout.setContentsMargins(0, 0, 0, 0)

                    # Test Button
                    btn = QPushButton(test_name)
                    btn.setStyleSheet("background-color: #926e55; color: white; border-radius: 10px; padding: 10px;")
                    btn.setFixedHeight(40)
                    btn.setFixedWidth(200)

                    # Status Label
                    status_label = QLabel("Status:")
                    status_label.setStyleSheet("background-color: white; border:1px solid black;")
                    status_label.setFixedWidth(300)
                    status_label.setAlignment(Qt.AlignCenter)

                    # Toggle Button
                    toggle_btn = QPushButton("▼")
                    toggle_btn.setFixedWidth(40)
                    toggle_btn.setFixedHeight(40)
                    toggle_btn.setStyleSheet("background-color: #634b3a; color: white; border-radius: 5px;")

                    # Store references
                    self.test_buttons[test_name] = btn
                    self.status_labels[test_name] = status_label
                    self.toggle_buttons[test_name] = toggle_btn

                    # Add widgets to row
                    row_layout.addWidget(btn)
                    row_layout.addWidget(status_label)
                    row_layout.addWidget(toggle_btn)
                    row_layout.addStretch()

                    # Create subfield frame (Initially Hidden)
                    detail_frame = QFrame()
                    detail_frame.setFrameShape(QFrame.StyledPanel)
                    detail_frame.setFrameShadow(QFrame.Sunken)
                    detail_frame.setStyleSheet("background-color: #8a6b54; border-radius: 5px; margin-left: 20px;")
                    detail_layout = QVBoxLayout(detail_frame)

                    # Load subfields from `body → key_pair`
                    self.detail_widgets[test_name] = {}

                    for body_section in test_body:
                        key_pairs = body_section.get("key_pair", [])

                        for field in key_pairs:
                            field_title = field["title"]
                            is_disabled = field.get("disable", False)
                            field_value = field.get("value", "")

                            # Create subfield row
                            subfield_layout = QHBoxLayout()

                            # Field Title Label
                            title_label = QLabel(f"{field_title}:")
                            title_label.setStyleSheet("color: white; background-color: transparent;")
                            title_label.setFixedWidth(200)

                            # Field Value Label
                            value_label = QLabel(field_value if field_value else "Not tested")
                            value_label.setStyleSheet("background-color: white; border: 1px solid black;")
                            value_label.setFixedWidth(300)
                            value_label.setAlignment(Qt.AlignCenter)

                            if is_disabled:
                                value_label.setEnabled(False)

                            # Store reference to the field
                            self.detail_widgets[test_name][field_title] = value_label

                            # Add to subfield layout
                            subfield_layout.addWidget(title_label)
                            subfield_layout.addWidget(value_label)
                            subfield_layout.addStretch()

                            # Add to detail frame
                            detail_layout.addLayout(subfield_layout)

                    # Hide detail frame initially
                    detail_frame.setVisible(False)
                    self.detail_frames[test_name] = detail_frame

                    # Connect toggle button
                    toggle_btn.clicked.connect(lambda checked, name=test_name: self.toggle_details(name))

                    # Connect test button
                    btn.clicked.connect(lambda checked, name=test_name: self.run_test(name))

                    # Add to main layout
                    self.main_layout.addWidget(row_frame)
                    self.main_layout.addWidget(detail_frame)

                self.main_layout.addStretch()

                self.scroll_area.setWidget(self.scroll_content)

                # Create a main layout for the status frame
                status_layout = QVBoxLayout(self.status_frame)
                status_layout.setContentsMargins(0, 0, 0, 0)

                # Add the scroll area to the status frame
                status_layout.addWidget(self.scroll_area)


        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load tests from JSON: {e}")


    def toggle_details(self, test_name):
        """Toggle visibility of the detail frame for a test"""
        detail_frame = self.detail_frames.get(test_name)
        if detail_frame:
            # Toggle visibility
            is_visible = detail_frame.isVisible()
            detail_frame.setVisible(not is_visible)
            
            # Update toggle button text
            toggle_btn = self.toggle_buttons.get(test_name)
            if toggle_btn:
                toggle_btn.setText("▲" if not is_visible else "▼")



    def run_test(self, test_name):
        """Run the test for the specified component"""
        # Here we would implement the actual test logic
        # For now, we'll just simulate a test
        
        # Update main status
        status_label = self.status_labels.get(test_name)
        if status_label:
            status_label.setText("Testing...")
            
            # In a real implementation, you would execute the test here
            # and update the status based on the result
            
            # Simulate a test running
            QtWidgets.QApplication.processEvents()
            import time
            time.sleep(0.5)  # Simulate test time
            
            # Update to success (in real code, check the actual result)
            status_label.setText("PASS")
            status_label.setStyleSheet("background-color: #90EE90; border:1px solid black;")
        
        # Update detailed fields
        detail_widgets = self.detail_widgets.get(test_name, {})
        for field_title, value_label in detail_widgets.items():
            value_label.setText("PASS")  # In real code, set the actual test result
            value_label.setStyleSheet("background-color: #90EE90; border:1px solid black;")
            
        # Auto-expand the details after testing
        detail_frame = self.detail_frames.get(test_name)
        if detail_frame and not detail_frame.isVisible():
            self.toggle_details(test_name)
    
    def test(self):
        """Run all tests"""
        self.saved_data.clear()  
        print("Saved data dictionary cleared.")
        for test_name in self.test_buttons:
            self.run_test(test_name)
        self.getdata()

    def __getPortDialoge(self):
        options = ["Serial Port", "BLE", "TCP"]
        selected_option, ok = QInputDialog.getItem(self, "Select Method", "Choose a Method:", options, editable=False)
        if not ok:  
            self.__toShow = True
            return
        if selected_option == "Serial Port":
            self.serial_thread = SerialThread()
            available_ports = self.serial_thread.available_ports()
            if not available_ports:
                QMessageBox.warning(self, "Warning", "No serial ports available!")
                self.__toShow = True
                return
            port, ok = QInputDialog.getItem(self, "Serial Ports", "Choose a Port:", available_ports, editable=False)
            if not ok or not port.strip(): 
                self.__toShow = True
                return
            self.serial_thread.set_port(port)
            print(f"Selected Serial Port: {port}")
            self.serial_thread.dataReceived.connect(self.doDataSegration)
            self.serial_thread.start()
        elif selected_option == "BLE":
            QMessageBox.information(self, "Device Not Connected", "No BLE device connected. Please connect and retry.")
            self.__toShow = True
        elif selected_option == "TCP":
            TCP_ports = ["4040", "4050", "4060"]
            selected_tcp_port, ok = QInputDialog.getItem(self, "TCP Ports", "Choose a Port:", TCP_ports, editable=False)
            if not ok or not selected_tcp_port.strip():
                self.__toShow = True
                return
            # .start_client(self,, int(selected_tcp_port))
            self.tcp_thread = TCPthread()
            self.tcp_thread.set_port(int(selected_tcp_port))
            self.tcp_thread.dataReceived.connect(self.doTCPDataSegration)
            self.tcp_thread.start()
            print(f"Selected TCP Port: {selected_tcp_port}")
            message = f"{HEADER}{chr(0xD7)}GET_IMEI"
            self.tcp_thread.send_request(message.encode("latin-1"))

    def doDataSegration(self,data):
        try:
            self.data_parsing(data.split("\xd7"))
        except Exception as e:
            print(e)

    def doTCPDataSegration(self,data):
        print(data,"TCP")
        if "IMEI" in data:
            imei_list = data.split(":")[1:]
            self.show_imei_selection_dialog(imei_list)
        elif ("$ZEN" in data):
            self.data_parsing(data.split(chr(0xD7)))

    def data_parsing(self,data):
        print(data)
        if data[0]!="$ZEN":
            return
        for x in data[2:-1]:
            try:
                key = str(x).split(chr(0xD5))
                print(key)
                key1=ord(str(key[0])[0])
                key2=ord(str(key[0])[1])
                value=str(key[1])
                box_value=self.current_status.get(key1)
                if box_value:
                    print("box_value",box_value)
                    print("key tro",key2)
                    box_inner=box_value.fields.get(key2)
                    if box_inner:

                        print(data[1])
                        if ord(data[1])==0xDB:
                            if box_inner.text()==value:
                                box_inner.setStyleSheet("QLineEdit { background-color: green; color: white;}")
                                print("Value is same")
                            else:
                                box_inner.setStyleSheet("QLineEdit { background-color: red; color: white;}")
                                print("Value is Not same")
                        else:
                            print("Value is same",value)
                            box_inner.setText(value)

            except:
                pass   

    def show_imei_selection_dialog(self, imei_list):
        if not imei_list:
            QMessageBox.warning(self, "No IMEIs Found", "No IMEI numbers received from the server.")
            return
        selected_imei, ok = QInputDialog.getItem(self, "Select IMEI", "Choose an IMEI Number:", imei_list, editable=False)
        if ok and selected_imei:
            print(f"Selected IMEI: {selected_imei}")
            self.selected_imei = selected_imei
            message=f"{HEADER}{chr(0xD7)}SELECTED_IMEI{chr(0xD7)}{self.selected_imei}{chr(0xD7)}{chr(0x34)}{chr(0xd1)}".encode('latin-1')
            self.tcp_thread.send_request(message)
        else:
            QMessageBox.warning(self, "No IMEIs Found", "No IMEI numbers received from the server.")
        return
    
    def getdata(self):
        data_to_send=f"{HEADER}{chr(0xD7)}{self.seed}{chr(0xD7)}{chr(0xDC)}{chr(0xD7)}{self.__get_parameters}{self.checksum}".encode('latin-1')
        print(data_to_send)
        if hasattr(self, 'serial_thread') and self.serial_thread:
            self.serial_thread.sendRequest(data_to_send)
        elif hasattr(self, 'tcp_thread') and self.tcp_thread:
            self.tcp_thread.send_request(data_to_send)
    
