import sys
import json
import socket
import requests
import os
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt ,QThread , pyqtSignal
from PyQt5.QtWidgets import QPushButton, QFileDialog, QVBoxLayout, QMessageBox, QFrame , QLabel ,QWidget, QGroupBox , QGridLayout , QStackedWidget , QInputDialog, QScrollArea 
from modules.utils import *
from modules.grpcard import *
from modules.serialRead import *
from modules.tcp import *

class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_device = None  # Ensure this is defined before usage
        self.device_buttons = {}
        self.selected_company = None
        self.initUI()
    
    def initUI(self):
        # Load the device selection screen first
        uic.loadUi("./UI/deviceselection.ui", self)
        self.setWindowTitle("Select a Device")
        
        self.device_buttons = {
            "Device A": self.findChild(QPushButton, "device1"),
            "Device B": self.findChild(QPushButton, "device2"),
            "Device C": self.findChild(QPushButton, "device3"),
            "Device D": self.findChild(QPushButton, "device4"),
        }
        
        for name, btn in self.device_buttons.items():
            if btn:
                btn.clicked.connect(lambda _, n=name: self.select_device(n))

        self.next_button = self.findChild(QPushButton, "nextButton")
        self.next_button.clicked.connect(self.load_choose_mode)

        self.show()


    def select_device(self, device_name):
        self.selected_device = device_name
        QMessageBox.information(self, "Device Selected", f"You selected: {device_name}")

        # Reset styles
        for btn in self.device_buttons.values():
            if btn:
                btn.setStyleSheet("background-color: #926e55; color: white; border-radius: 10px;")
        
        # Highlight selected button
        if self.device_buttons.get(device_name):
            self.device_buttons[device_name].setStyleSheet("background-color: #634b3a; color: white; border-radius: 10px; border: 50px solid red;")

    def load_choose_mode(self):
        if not self.selected_device:
            QMessageBox.warning(self, "No Device Selected", "Please select a device before proceeding.", QMessageBox.Ok)
            return
        dialog = QtWidgets.QDialog(self)
        uic.loadUi("./UI/choosemode.ui", dialog)
        self.setWindowTitle("Select Mode")

        config_button = self.findChild(QPushButton, "configButton")
        test_button = self.findChild(QPushButton, "testButton")

        config_button.clicked.connect(lambda: self.load_company_selection() or dialog.accept())
        test_button.clicked.connect(lambda: self.load_test_screen() or dialog.accept())

        dialog.exec_() 

    def load_company_selection(self):
        uic.loadUi("./UI/companyselection.ui", self)
        self.setWindowTitle("Select Company")

        # Fetch companies from DB (Placeholder for now)
        scroll_area = self.findChild(QtWidgets.QScrollArea, "scrollArea")
        scroll_area_widget = scroll_area.findChild(QtWidgets.QWidget, "scrollAreaWidgetContents")
        company_layout = scroll_area_widget.findChild(QtWidgets.QVBoxLayout, "companyLayout")

        while company_layout.count():
            child = company_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Fetch company data from the JSON server
        try:
            response = requests.get("http://127.0.0.1:60171/api/companies")
            response.raise_for_status()  # Raises an error for bad responses (4xx, 5xx)
            companies = response.json()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch companies: {e}")
            return

        self.company_buttons = {}

    # Dynamically add buttons for each company
        for company in companies:
            company_name = company["companyname"]
            company_logo = company["image"]

            # Create a button for the company
            button = QPushButton(company_name)
            button.setStyleSheet("background-color: #926e55; color: white; border-radius: 10px; padding: 10px;")
            button.setMinimumHeight(60)

            # Load the company logo (if valid)
            pixmap = QPixmap()
            if pixmap.loadFromData(requests.get(company_logo).content):
                button.setIcon(QIcon(pixmap))
                button.setIconSize(QtCore.QSize(50, 50))

            # Store button reference
            self.company_buttons[company_name] = button
            button.clicked.connect(lambda _, n=company_name: self.load_homepage(n))

            # Add button to layout
            company_layout.addWidget(button)

            self.show()

    def load_test_screen(self):
        uic.loadUi("./UI/testscreen.ui", self)
        self.setWindowTitle("Test Mode")
        QMessageBox.information(self, "Test Mode", "Entering Test Mode.")
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
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: #743d3d; border: none;")

        scroll_content = QWidget()
        main_layout = QVBoxLayout(scroll_content)
        main_layout.setSpacing(10)

        # UI Element Storage
        self.test_buttons = {}      # Main test buttons
        self.status_labels = {}     # Main status labels
        self.detail_frames = {}     # Frames to hold detailed subfields
        self.detail_widgets = {}    # Dictionary of dictionaries for subfield widgets
        self.toggle_buttons = {}    # Expand/collapse buttons

        # Load updated JSON structure
        with open(f'{SCAN_DIR}/test/main.json', 'r') as file:
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
                main_layout.addWidget(row_frame)
                main_layout.addWidget(detail_frame)

            main_layout.addStretch()

            scroll_area.setWidget(scroll_content)

            # Create a main layout for the status frame
            status_layout = QVBoxLayout(self.status_frame)
            status_layout.setContentsMargins(0, 0, 0, 0)

            # Add the scroll area to the status frame
            status_layout.addWidget(scroll_area)

        self.show()


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
        for test_name in self.test_buttons:
            self.run_test(test_name)



    
    def load_homepage(self, company_name):
        if not self.selected_device:
            QMessageBox.warning(self, "No Device Selected", "Please select a device before proceeding.", QMessageBox.Ok)
            return
        self.selected_company = company_name
        uic.loadUi("./UI/homepage.ui", self)
        self.setWindowTitle("ZENTRACK")
        self.setWindowIcon(QIcon(f"{LOGO_DIR}/zentrack-favicon-black.png"))
        self.setAutoFillBackground(True)
        self.saverbtn = self.findChild(QPushButton , 'saverbtn')
        self.saverbtn.clicked.connect(self.save_to_device)
        self.uploadbtn = self.findChild(QPushButton , 'uploadbtn')
        self.uploadbtn.clicked.connect(self.upload_data)
        self.downloadbtn = self.findChild(QPushButton , 'downloadbtn')
        self.downloadbtn.clicked.connect(self.download_data)
        self.getdevicebtn = self.findChild(QPushButton , 'getdevicebtn')
        self.getdevicebtn.clicked.connect(self.get_device_data)
        self.frame = self.findChild(QFrame , 'navlyout')
        self.container = self.findChild(QWidget, 'page1')
        layout = QVBoxLayout(self.frame)
        self.frame.setLayout(layout)
        self.saved_data = {}
        self.seed="1234"
        self.checksum="4\xd1"
        self.current_status={}
        with open (f'{SCAN_DIR}/main.json', 'r' ) as file:
            jsndta = json.load(file)
        if jsndta :
            for item in jsndta['navbtn']:
                btn = QPushButton(item['name'])
                layout.addWidget(btn)
                layout.layout().setAlignment(Qt.AlignTop)
                btn.clicked.connect(lambda checked , d = item:self.shwda(d))
        QMessageBox.information(self, "Device Loaded", f"Welcome! You selected {self.selected_device}.")
        self.__getPortDialoge()
    def get_device_data(self):
        self.saved_data.clear()  
        print("Saved data dictionary cleared.")
        for field_code, grpbox in self.current_status.items():
            for item_code, item in grpbox.fields.items():
                item.clear() 
        self.getdata()
        print("All input fields have been cleared.")
    def download_data(self):
        if not self.saved_data:
            QMessageBox.warning(self, "Warning", "No data to download! Please save something first.")
            return
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "JSON Files (*.json);;All Files (*)", options=options)
        if file_path:  
            with open(file_path, 'w') as json_file:
                json.dump(self.saved_data, json_file, indent=4)  
            QMessageBox.information(self, "Success", f"Data saved successfully to {file_path}")
            print(f"Data downloaded to {file_path}")
    def upload_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "JSON Files (*.json);;All Files (*)")
        if not file_path:  
            return
        try:
            with open(file_path, 'r') as json_file:
                uploaded_data = json.load(json_file)  
            self.saved_data.update(uploaded_data)
            for field_code, grpbox in self.current_status.items():
                if str(field_code) in uploaded_data: 
                    for item_code, item in grpbox.fields.items():
                        if str(item_code) in uploaded_data[str(field_code)]:  
                            item.setText(uploaded_data[str(field_code)][str(item_code)]) 
                            print(f"Updated Field: [{field_code}][{item_code}] → {uploaded_data[str(field_code)][str(item_code)]}")
            QMessageBox.information(self, "Success", "Data uploaded and fields updated successfully!")
            print(f"Data loaded from {file_path}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load JSON: {e}")
            print(f"Error loading JSON: {e}")
    def save_to_device(self):
        reply = QMessageBox.question(self, 'Confirmation',"Are you- sure you want to save?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            parameter = ""
            for field_code, grpbox in self.current_status.items():
                for item_code,item in grpbox.fields.items():
                    if not item.isEnabled():
                        continue
                    text = item.text().strip()
                    if len(text) > 0:
                        parameter += f"{chr(field_code)}{chr(item_code)}{chr(0xD5)}{text}{chr(0xD7)}"
                        if str(field_code) not in self.saved_data:
                            self.saved_data[str(field_code)] = {}
                        self.saved_data[str(field_code)][str(item_code)] = text 
            if len(parameter)==0:
                QMessageBox.information(self, 'Confirmation',"No Fields Available For Save ", QMessageBox.Ok)
                return
            print("Saved Data Dictionary:", self.saved_data)
            data_to_send=f"{HEADER}{chr(0xD7)}{self.seed}{chr(0xD7)}{chr(0xDB)}{chr(0xD7)}{parameter}{self.checksum}".encode('latin-1') 
            print("going bro",data_to_send,len(data_to_send))
            if hasattr(self, 'serial_thread') and self.serial_thread:
                self.serial_thread.sendRequest(data_to_send)
                message = "Saved"
                QMessageBox.information(self, 'Confirmation', message, QMessageBox.Ok)
            elif hasattr(self, 'tcp_thread') and self.tcp_thread:
                self.tcp_thread.send_request(data_to_send)
            else:
                QMessageBox.warning(self, "Error", "No communication method selected!")
        else:
            print("Action cancelled.")
    def empty_layout(self,layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater() 
    def shwda(self,data):
        print(data)
        self.current_status={}
        data=data['filepath']
        self.empty_layout(self.container.layout())
        with open (data, 'r' ) as file:
            self.btndta = json.load(file)    
        legnth = len(self.btndta)//2+1
        self.__get_parameters=""
        for i,content in enumerate(self.btndta):
            grpbox = Grpcard(content)
            field_code=content.get("code")
            if field_code:
                self.current_status[field_code]=grpbox
                for item_code  in grpbox.fields.keys():
                    print(hex(field_code),hex(item_code))
                    self.__get_parameters+=f"{chr(field_code)}{chr(item_code)}{chr(0xD7)}"
                    if str(field_code) in self.saved_data:
                        if str(item_code) in self.saved_data[str(field_code)]:
                            grpbox.fields[item_code].setText(self.saved_data[str(field_code)][str(item_code)])
                            print(f"Restoring Field: [{field_code}][{item_code}] → {self.saved_data[str(field_code)][str(item_code)]}")
            row = i // legnth
            col = i % legnth
            self.container.layout().addWidget(grpbox, row, col)
    def getdata(self):
        data_to_send=f"{HEADER}{chr(0xD7)}{self.seed}{chr(0xD7)}{chr(0xDA)}{chr(0xD7)}{self.__get_parameters}{self.checksum}".encode('latin-1')
        print(data_to_send)
        if hasattr(self, 'serial_thread') and self.serial_thread:
            self.serial_thread.sendRequest(data_to_send)
        elif hasattr(self, 'tcp_thread') and self.tcp_thread:
            self.tcp_thread.send_request(data_to_send)
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
            
        # try:
        #     self.data_parsing(data.split("\xd7"))
        # except Exception as e:
        #     print(e)
        # print(data)
class SerialThread(QThread,SerialRead):
    dataReceived = pyqtSignal(str)
    def run(self):
        super(SerialRead, self)
    def set_port(self,port):
        self.start_serial(port,self.__serialCallback)
    def __serialCallback(self, data):
        try:
            self.dataReceived.emit(data)
        except Exception as e:
            print("Error in conversion ",e)
class TCPthread(QThread,TCP):
    dataReceived = pyqtSignal(str)
    def run(self):
        super(TCP, self)
    def set_port(self,port):
        self.start_client(port,self.__tcpCallback)
    def __tcpCallback(self, data):
        try:
            self.dataReceived.emit(data)
        except Exception as e:
            print("Error in conversion ",e)
            
app = QtWidgets.QApplication(sys.argv)
window = MainApp()
window.showMaximized()
sys.exit(app.exec_())
