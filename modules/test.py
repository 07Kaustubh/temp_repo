import json
from PyQt5.QtWidgets import QPushButton, QLabel, QVBoxLayout, QMessageBox, QFrame, QMainWindow
from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea, QWidget, QHBoxLayout
from PyQt5.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QScrollArea, QWidget, QMainWindow
from modules.base_screen import BaseScreen
import os

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
        for test_name in self.test_buttons:
            self.run_test(test_name)

