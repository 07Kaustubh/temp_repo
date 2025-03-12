from PyQt5.QtWidgets import QPushButton, QMessageBox, QDialog
from PyQt5 import uic, QtWidgets
from PyQt5 import QtCore

class DeviceSelection(QtWidgets.QMainWindow):
    """Handles device selection screen."""

    selection_complete = QtCore.pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        uic.loadUi("./UI/deviceselection.ui", self)
        self.setWindowTitle("Select a Device")
        self.selected_device = None
        
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
        self.next_button.clicked.connect(self.confirm_selection)

    def select_device(self, device_name):
        """Selects a device and highlights it."""
        self.selected_device = device_name
        QMessageBox.information(self, "Device Selected", f"You selected: {device_name}")

        # Reset button styles
        for btn in self.device_buttons.values():
            if btn:
                btn.setStyleSheet("background-color: #926e55; color: white; border-radius: 10px;")

        # Highlight selected button
        if self.device_buttons.get(device_name):
            self.device_buttons[device_name].setStyleSheet("background-color: #634b3a; color: white; border-radius: 10px; border: 50px solid red;")

    def confirm_selection(self):
        """Confirms device selection and emits signal to proceed."""
        if self.selected_device:
            self.selection_complete.emit(self.selected_device)  # Emit signal with selected device
        elif not self.selected_device:
            QMessageBox.warning(self, "No Device Selected", "Please select a device before proceeding.", QMessageBox.Ok)
            return
