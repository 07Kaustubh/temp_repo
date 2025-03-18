import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QPushButton, QMessageBox
from modules.home import HomeScreen
from modules.test import TestScreen
from modules.device_selection import DeviceSelection
from modules.company_selection import CompanySelectionScreen

class MainApp(QtWidgets.QMainWindow):
    """Manages screen transitions, device selection, and communication handling."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Application")      

        # Initialize all screens
        self.device_selection = DeviceSelection()
        self.company_screen = CompanySelectionScreen()
        self.home_screen = None
        self.test_screen = TestScreen()

        self.initUI()

    def initUI(self):
        """Starts with the device selection screen."""
        self.setCentralWidget(self.test_screen)
        self.device_selection.selection_complete.connect(self.load_choose_mode)

    def load_company_selection(self):
        """Loads the Company Selection Screen after selecting a device."""
        self.setCentralWidget(self.company_screen)

    def load_home_screen(self, company_name):
        """Loads the Home Screen after company selection."""

        if self.home_screen is None:
            self.home_screen = HomeScreen()
                    
        self.setCentralWidget(self.home_screen)
        QtWidgets.QMessageBox.information(self, "Company Selected", f"Welcome to {company_name}!")

    def switch_to_test(self):
        """Switches to the Test Screen."""
        self.setCentralWidget(self.test_screen)

    def switch_to_home(self):
        """Switches back to the Home Screen."""
        self.setCentralWidget(self.home_screen)

    def load_choose_mode(self):
        """Prompts user to choose between Config Mode or Test Mode."""
               
        dialog = QtWidgets.QDialog(self)
        uic.loadUi("./UI/choosemode.ui", dialog)
        self.setWindowTitle("Select Mode")

        config_button = dialog.findChild(QPushButton, "configButton")
        test_button = dialog.findChild(QPushButton, "testButton")

        config_button.clicked.connect(lambda: (self.load_company_selection(), dialog.accept()))
        test_button.clicked.connect(lambda: (self.switch_to_test(), dialog.accept()))

        dialog.exec_()
