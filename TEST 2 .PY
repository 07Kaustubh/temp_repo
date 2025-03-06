from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QFileDialog
import json
import sys

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Creating line edits
        self.name_field = QLineEdit(self)
        self.age_field = QLineEdit(self)
        self.email_field = QLineEdit(self)

        # Button to load data
        self.load_button = QPushButton("Load Data", self)
        self.load_button.clicked.connect(self.load_data)

        # Add widgets to layout
        layout.addWidget(self.name_field)
        layout.addWidget(self.age_field)
        layout.addWidget(self.email_field)
        layout.addWidget(self.load_button)

        self.setLayout(layout)
        self.setWindowTitle("Auto Fill Fields")
        self.show()

    def load_data(self):
        # Open file dialog to select JSON file
        file_name, _ = QFileDialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json);;All Files (*)")

        if file_name:
            try:
                with open(file_name, "r") as file:
                    data = json.load(file)

                # Fill fields based on JSON keys
                self.name_field.setText(data.get("name", ""))
                self.age_field.setText(str(data.get("age", "")))
                self.email_field.setText(data.get("email", ""))

            except Exception as e:
                print("Error loading JSON:", e)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
