import sys
import json
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt , pyqtSignal
from PyQt5.QtWidgets import QPushButton,QLineEdit, QDialog ,QVBoxLayout, QHBoxLayout, QFrame , QFormLayout ,QLabel ,QWidget, QGroupBox , QGridLayout , QStackedWidget
from modules.utils import *
class ClickInput(QLineEdit):
    # A QLabel subclass that can handle clicks
    clicked = pyqtSignal()  # Signal to handle clicks
    def __init__(self,parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:  # Check if left button is pressed
            self.clicked.emit()  # Emit the click signal

class NewWindow(QDialog):
    def __init__(self,input_text):
        super().__init__()
        uic.loadUi("./UI/combox.ui", self)
        self.setWindowTitle("Config_Can")
        self.pushButton.clicked.connect(lambda:self.collect_data(input_text))
        self.dropdown1_mapping = {"Extended ID": 2, "Standard ID": 1}
        self.dropdown2_mapping = {"Range": 1, "Dual": 2, "Mask": 3}
        print(input_text.text())
        

    def collect_data(self,input_text):
        dropdown1_value = self.comboBox1.currentText()
        dropdown2_value = self.comboBox2.currentText()
        dropdown1_mapped = self.dropdown1_mapping.get(dropdown1_value, "Unknown")
        dropdown2_mapped = self.dropdown2_mapping.get(dropdown2_value, "Unknown")
        lineedit1_value = self.lineEdit1.text()
        lineedit2_value = self.lineEdit2.text()
        result_string = f"{dropdown1_mapped}{chr(0xD9)}{dropdown2_mapped}{chr(0xD9)}{lineedit1_value}{chr(0xD9)}{lineedit2_value}"
        print(result_string)
        print(input_text.text())
        input_text.setText(result_string)
        self.close()


class NewcanWindow(QDialog):
    def __init__(self,input_text):
        super().__init__()
        uic.loadUi("./UI/cannum.ui", self)
        self.setWindowTitle("Config_Nbr")
        self.pushButton.clicked.connect(lambda:self.collect_data(input_text))
        print(input_text.text())

    def collect_data(self,input_text):
        lineedit1_value = self.lineEdit1.text()
        lineedit2_value = self.lineEdit2.text()
        result_string = f"{lineedit1_value}{chr(0xD9)}{lineedit2_value}"
        print(result_string)
        print(input_text.text())
        input_text.setText(result_string)
        self.close()

class NewcantxWindow(QDialog):
    def __init__(self,input_text):
        super().__init__()
        uic.loadUi("./UI/cantx.ui", self)
        self.setWindowTitle("Config_tx")
        self.pushButton.clicked.connect(lambda:self.collect_data(input_text))
        self.dropdown1_mapping = {"Extended ID": 2, "Standard ID": 1}
        print(input_text.text())

    def collect_data(self,input_text):
        dropdown1_value = self.comboBox1.currentText()
        dropdown1_mapped = self.dropdown1_mapping.get(dropdown1_value, "Unknown")
        lineedit1_value = self.lineEdit1.text()
        lineedit2_value = self.lineEdit2.text()
        result_string = f"{dropdown1_mapped}{chr(0xD9)}{lineedit1_value}{chr(0xD9)}{lineedit2_value}"
        print(result_string)
        print(input_text.text())
        input_text.setText(result_string)
        self.close()

class NewCanWakeupWindow(QDialog):
    def __init__(self, input_text):
        super().__init__()
        uic.loadUi("./UI/canwakeup.ui", self)
        self.setWindowTitle("CAN Wakeup Config")
        self.config_id_type_mapping = {"Extended ID": 2, "Standard ID": 1}
        self.config_filter_type_mapping = {"Range": 1, "Dual": 2, "Mask": 3}
        self.saveButton.clicked.connect(lambda:self.collect_data(input_text))

    def collect_data(self, input_text):
        wakeup_state = self.wakeupState.currentText()
        config_id_type = self.configIdType.currentText()
        config_id_type_mapped = self.config_id_type_mapping.get(config_id_type, "Unknown")
        config_filter_type = self.configFilterType.currentText()
        config_filter_type_mapped = self.config_filter_type_mapping.get(config_filter_type, "Unknown")
        config_filter_1 = self.configFilter1.text()
        config_filter_2 = self.configFilter2.text()
        extended_id_count = self.extendedIdCount.text()
        standard_id_count = self.standardIdCount.text()
        result_string = (f"{wakeup_state}{chr(0xD9)}{config_id_type_mapped}{chr(0xD9)}{config_filter_type_mapped}{chr(0xD9)}{config_filter_1}{chr(0xD9)}{config_filter_2}{chr(0xD9)}{extended_id_count}{chr(0xD9)}{standard_id_count}")
        print(result_string)
        print(input_text.text())
        input_text.setText(result_string)
        self.close()
        
class Grpcard(QFrame):
    def open_new_window(self,input_text):
        self.new_window = NewWindow(input_text)
        print(input_text.text())
        self.new_window.exec_()
    def open_newcan_window(self,input_text):
        self.new_window = NewcanWindow(input_text)
        print(input_text.text())
        self.new_window.exec_()
    def open_newcan_txwindow(self,input_text):
        self.new_window = NewcantxWindow(input_text)
        print(input_text.text())
        self.new_window.exec_()
    def open_can_wakeup_window(self, input_text):
        self.new_window = NewCanWakeupWindow(input_text)
        self.new_window.exec_()
    def __init__(self,data):
        super().__init__()
        uic.loadUi("./UI/grpcard.ui",self)
        self.box = self.findChild(QGroupBox , 'groupBox')
        self.box.setTitle(data['title'])
        self.data = data
        self.fields={}
        self.box.layout().setAlignment(Qt.AlignTop)
        self.add_element()
    def add_label(self,data):
        frame = QFrame()
        frame.setLayout(QHBoxLayout())
        print(data)
        for label_data in data:
            label = QLabel()
            label.setText(label_data['title'])
            frame.layout().addWidget(label)
        self.box.layout().addWidget(frame)
    def add_btn(self,data):
        frame = QFrame()
        frame.setLayout(QGridLayout())
        for i,button_data in enumerate(data):
            row = i//2
            col = i%2
            button = QPushButton()
            button.setText(button_data['title'])
            frame.layout().addWidget(button,row,col)
        self.box.layout().addWidget(frame)
    def add_input(self,data):
        i = 0
        for input_data in data:
            code =input_data.get('code')
            if code:
                frame = QFrame()
                frame.setLayout(QHBoxLayout())
                label = QLabel()
                label.setMinimumWidth(100)
                label.setText(input_data['title'])
                input_box = QLineEdit()
                if input_data.get("input_type","na") == 'can_data' :
                    print("can data")
                    input_box = ClickInput()
                    current_input_box = input_box  # Capture the current instance
                    input_box.clicked.connect(lambda current_input_box=current_input_box: self.open_new_window(current_input_box))
                if input_data.get("input_type","na") == 'can_Nbr' :
                    print("can nbr")
                    input_box = ClickInput()
                    current_input_box = input_box  # Capture the current instance
                    input_box.clicked.connect(lambda current_input_box=current_input_box: self.open_newcan_window(current_input_box))
                if input_data.get("input_type","na") == 'can_tx' :
                    print("can tx")
                    input_box = ClickInput()
                    current_input_box = input_box  # Capture the current instance
                    input_box.clicked.connect(lambda current_input_box=current_input_box: self.open_newcan_txwindow(current_input_box))
                input_box.setPlaceholderText(input_data['value'])
                if input_data.get("input_type") == 'can_wakeup':
                    input_box = ClickInput()
                    current_input_box = input_box  # Capture the current instance
                    input_box.clicked.connect(lambda box=current_input_box: self.open_can_wakeup_window(box))
                if input_data.get("disable"):
                    input_box.setDisabled(True)
                self.fields[code]=input_box
                frame.layout().addWidget(label)
                frame.layout().addWidget(input_box)                         
                self.box.layout().addWidget(frame)

    def add_element(self):
        print(self.data['body'])
        for rows in self.data[BODY]:
            for key,row_data in rows.items():
                # print(key)
                if key == 'label':
                    self.add_label(row_data)
                elif key == 'button':
                    self.add_btn(row_data)
                elif key == 'input':
                    self.add_input(row_data)
def Send_data(Key , F_type , d_packet , Checksum):
    Key = ''.join(f'{ord(c):02x}' for c in Key)
    F_type = ''.join(f'{ord(c):02x}' for c in F_type)
    d_packet = ''.join(f'{ord(c):02x}' for c in d_packet)
    Checksum = ''.join(f'{ord(c):02x}' for c in Checksum)
    tail = "*"
    sendta = f"{Key},{F_type},{d_packet},{Checksum}{tail}"
    return sendta


