import requests
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QMessageBox, QScrollArea, QWidget, QLabel, QMainWindow
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon
from modules.base_screen import BaseScreen
from PyQt5 import uic

class CompanySelectionScreen(QMainWindow):
    """Handles company selection by fetching data from API and dynamically generating buttons."""

    def __init__(self):
        super().__init__()  # No arguments to QMainWindow
        uic.loadUi("./UI/companyselection.ui", self)  # Load UI separately
        self.setWindowTitle("Select Company")

        self.api_url = "http://127.0.0.1:62716/api/companies"  # API to fetch company data
        self.company_buttons = {}
        self.initUI()

    def initUI(self):
        """Initialize UI components and fetch company list dynamically."""
        self.scroll_area = self.findChild(QScrollArea, "scrollArea")
        self.scroll_area_widget = self.scroll_area.findChild(QWidget, "scrollAreaWidgetContents")
        self.company_layout = self.scroll_area_widget.findChild(QVBoxLayout, "companyLayout")
        
        self.fetch_companies()

    def fetch_companies(self):
        """Fetch company names from the API and generate buttons dynamically."""
        try:
            response = requests.get(self.api_url)
            response.raise_for_status()  # Raises an error for 4xx and 5xx responses
            companies = response.json()

            if not companies:
                QMessageBox.warning(self, "No Companies", "No company data available.")
                return

            self.populate_company_buttons(companies)

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch companies: {e}")

    def populate_company_buttons(self, companies):
        """Dynamically creates buttons for each company."""
        # Clear previous buttons if any
        while self.company_layout.count():
            child = self.company_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for company in companies:
            company_name = company.get("companyname", "Unknown Company")
            company_logo = company.get("image", "")

            # Create a button for each company
            button = QPushButton(company_name)
            button.setStyleSheet(
                "background-color: #926e55; color: white; border-radius: 10px; padding: 10px;"
            )
            button.setMinimumHeight(60)

            # Load the company logo if available
            if company_logo:
                pixmap = QPixmap()
                if pixmap.loadFromData(requests.get(company_logo).content):
                    button.setIcon(QIcon(pixmap))
                    button.setIconSize(QSize(50, 50))

            # Store button reference
            self.company_buttons[company_name] = button
            button.clicked.connect(lambda _, n=company_name: self.select_company(n))

            # Add button to the layout
            self.company_layout.addWidget(button)

    def select_company(self, company_name):
        """Handles company selection and switches to HomeScreen."""
        QMessageBox.information(self, "Company Selected", f"You selected: {company_name}")
        # Assuming `MainApp` has a method `load_home_screen(company_name)`
        self.parent().load_home_screen(company_name)
