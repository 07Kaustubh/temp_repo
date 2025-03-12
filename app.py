from modules.main_app import MainApp
from PyQt5 import QtWidgets
import sys

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.showMaximized()
    sys.exit(app.exec_())
