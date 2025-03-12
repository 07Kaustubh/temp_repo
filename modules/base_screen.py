from PyQt5 import QtWidgets, uic

class BaseScreen(QtWidgets.QWidget):
    """Base class for all screens with common functionality."""
    
    def __init__(self, ui_path, title):
        super().__init__()
        uic.loadUi(ui_path, self)
        self.setWindowTitle(title)
        
        # Ensure child classes implement initUI()
        if not hasattr(self, "initUI") or not callable(getattr(self, "initUI")):
            raise NotImplementedError("Subclasses of BaseScreen must implement initUI()")
        
        self.initUI()  # Call the UI initialization

    def show_message(self, title, message, icon=QtWidgets.QMessageBox.Information):
        """Display a message box."""
        msg_box = QtWidgets.QMessageBox()
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()
