import json
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt ,QThread , pyqtSignal
from PyQt5.QtWidgets import QPushButton, QFileDialog, QVBoxLayout, QMessageBox, QFrame , QLabel ,QWidget, QGroupBox , QGridLayout , QStackedWidget , QInputDialog, QMainWindow 
from modules.communication import SerialThread, TCPthread
from modules.grpcard import Grpcard
from modules.base_screen import BaseScreen
from modules.utils import*
from modules.serialRead import *
from modules.tcp import *

class HomeScreen(QMainWindow):
    """Handles the Home screen functionality with dynamic UI generation."""

    def __init__(self):
        super().__init__()
        uic.loadUi("./UI/homepage.ui", self)
        self.setWindowTitle("ZENTRACK")
        self.setWindowIcon(QIcon("./LOGO/zentrack-favicon-black.png"))
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
        with open ('./json/SCAN/main.json', 'r' ) as file:
            jsndta = json.load(file)
        if jsndta :
            for item in jsndta['navbtn']:
                btn = QPushButton(item['name'])
                layout.addWidget(btn)
                layout.layout().setAlignment(Qt.AlignTop)
                btn.clicked.connect(lambda checked , d = item:self.shwda(d))
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
        # print(data)
        if data[0]!="$ZEN":
            return
        print(data)
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


