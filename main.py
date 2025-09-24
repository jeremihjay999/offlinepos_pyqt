import sys
import os
from datetime import datetime
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from db import POSDatabase
from config import TAX_INCLUSIVE
from payment_dialog import SplitPaymentDialog
from dialogs import AddUserDialog, EditUserDialog
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import user_auth
from dialogs import FirstTimeSetupDialog, VerifyOTPDialog, CreateUserDialog, ResetPasswordDialog

class LoginDialog(QDialog):
    def __init__(self, db: POSDatabase):
        super().__init__()
        self.db = db
        self.user = None
        self.buttons = []
        self.focus_widgets = []
        self.current_focus = 0
        self.init_ui()
    
    def keyPressEvent(self, event):
        # Handle arrow key navigation
        if event.key() == Qt.Key_Down:
            self.navigate(1)
        elif event.key() == Qt.Key_Up:
            self.navigate(-1)
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if self.focusWidget() in [self.login_btn, self.cancel_btn]:
                self.focusWidget().click()
            else:
                self.navigate(1)
        else:
            super().keyPressEvent(event)
    
    def navigate(self, direction):
        self.current_focus = (self.current_focus + direction) % len(self.focus_widgets)
        self.focus_widgets[self.current_focus].setFocus()
        
    def init_ui(self):
        self.setWindowTitle("POS System - Login")
        self.setFixedSize(400, 250)
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #333;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover, QPushButton:focus {
                background-color: #0056b3;
                border: 2px solid #003d82;
            }
            QPushButton:focus {
                border: 2px solid #0056b3;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Point of Sale System")
        title.setAlignment(Qt.AlignCenter)
        font = title.font()
        font.setBold(True)
        title.setFont(font)
        title.setStyleSheet("margin: 20px;")
        layout.addWidget(title)
        
        # Form
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        form_layout.addRow("Username:", self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter password")
        form_layout.addRow("Password:", self.password_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.login)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.login_btn)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Info label
        info = QLabel("Default: admin / admin123")
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet("color: #666; margin-top: 10px;")
        layout.addWidget(info)
        
        self.setLayout(layout)
        
        # Set up focus navigation
        self.focus_widgets = [
            self.username_input,
            self.password_input,
            self.login_btn,
            self.cancel_btn
        ]
        
        # Set initial focus
        self.username_input.setFocus()
        self.current_focus = 0
        
        # Enable tab and return key navigation
        for i, widget in enumerate(self.focus_widgets):
            widget.setFocusPolicy(Qt.StrongFocus)
            # Only connect returnPressed for QLineEdit widgets
            if isinstance(widget, QLineEdit) and i < len(self.focus_widgets) - 1:
                widget.returnPressed.connect(lambda: self.navigate(1))
        
    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password")
            self.username_input.setFocus()
            self.current_focus = 0
            return

        if username == "admin" and password == "admin123":
            self.handle_password_reset()
            return

        user = self.db.authenticate_user(username, password)
        if user:
            # On successful login, verify machine fingerprint
            syscfg_data = user_auth.read_syscfg_file()
            if syscfg_data and syscfg_data.get("machine_fingerprint") == user_auth.get_machine_fingerprint():
                self.user = user
                self.accept()
            else:
                QMessageBox.critical(self, "Activation Error", "This software is not activated for this machine.")
                # Optionally, you could clear the syscfg file here to force reactivation
                # os.remove(user_auth.get_syscfg_path())
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid username or password")
            self.password_input.clear()
            self.password_input.setFocus()
            self.current_focus = 1

    def handle_password_reset(self):
        if not user_auth.check_syscfg_exists():
            QMessageBox.critical(self, "Error", "System not activated. Password reset is not available.")
            return

        syscfg_data = user_auth.read_syscfg_file()
        if not syscfg_data:
            QMessageBox.critical(self, "Error", "Could not read activation file.")
            return

        phone_number = syscfg_data.get("phone_number")

        # Request OTP for password reset
        response = user_auth.send_activation_request("Password Reset", phone_number)
        if not response.get("success"):
            QMessageBox.critical(self, "Error", response.get("message", "Failed to send OTP for password reset."))
            return

        reset_dialog = ResetPasswordDialog(phone_number)
        if reset_dialog.exec() == QDialog.Accepted:
            otp, new_username, new_password = reset_dialog.get_data()

            if not all([otp, new_username, new_password]):
                QMessageBox.critical(self, "Error", "All fields are required.")
                return

            # Verify OTP
            verify_response = user_auth.verify_otp(phone_number, otp)
            if not verify_response.get("success"):
                QMessageBox.critical(self, "Error", verify_response.get("message", "OTP verification failed."))
                return

            # In a real application, you would likely want to find the user by phone number
            # or have a more robust way to identify the user to update.
            # For this example, we'll just create a new user or update an existing one.
            # This is a simplification.
            user = self.db.get_user_by_username(new_username)
            if user:
                if self.db.reset_password(user['id'], new_password):
                     QMessageBox.information(self, "Success", "Password updated successfully!")
                else:
                    QMessageBox.critical(self, "Error", "Failed to update password.")
            else:
                if self.db.create_user(new_username, new_password, "admin", ["Can access sales tab", "Can access products tab", "Can access reports tab", "Can access settings tab"]):
                    QMessageBox.information(self, "Success", "New user created successfully!")
                else:
                    QMessageBox.critical(self, "Error", "Failed to create new user.")

            # Re-write the syscfg file to update the fingerprint if it has changed
            machine_fingerprint = user_auth.get_machine_fingerprint()
            user_auth.write_syscfg_file(phone_number, machine_fingerprint)

        self.username_input.clear()
        self.password_input.clear()
        self.username_input.setFocus()

class ShiftDialog(QDialog):
    def __init__(self, db: POSDatabase, user_id: int):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.opening_cash = 0.0
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Start Shift")
        self.setFixedSize(300, 150)
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Enter opening cash amount:"))
        
        self.cash_input = QLineEdit()
        self.cash_input.setPlaceholderText("0.00")
        layout.addWidget(self.cash_input)
        
        buttons = QHBoxLayout()
        
        start_btn = QPushButton("Start Shift")
        start_btn.clicked.connect(self.start_shift)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        buttons.addWidget(start_btn)
        buttons.addWidget(cancel_btn)
        
        layout.addLayout(buttons)
        self.setLayout(layout)
        
    def start_shift(self):
        try:
            self.opening_cash = float(self.cash_input.text() or "0")
            self.accept()
        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter a valid number")

class POSMainWindow(QMainWindow):
    def __init__(self, app, db: POSDatabase, user: dict):
        super().__init__()
        self.app = app
        self.db = db
        self.user = user
        self.should_logout = False
        self.current_shift = None
        self.cart_items = []
        
        # Check for active shift or start new one
        self.check_shift()
        
        self.init_ui()
        
    def check_shift(self):
        """Check for active shift or prompt to start new one"""
        active_shift = self.db.get_active_shift(self.user['id'])
        if active_shift:
            self.current_shift = active_shift
        else:
            # Start new shift
            shift_dialog = ShiftDialog(self.db, self.user['id'])
            if shift_dialog.exec() == QDialog.Accepted:
                shift_id = self.db.start_shift(self.user['id'], shift_dialog.opening_cash)
                self.current_shift = self.db.get_active_shift(self.user['id'])
            else:
                sys.exit()
                
    def init_ui(self):
        store_name = self.db.get_setting('store_name')
        self.setWindowTitle(f"{store_name} - POS System - {self.user['username']} ({self.user['role'].title()})")
        self.setGeometry(100, 100, 1400, 800)
        
        # Apply modern styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e9ecef;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #007bff;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
        
        # Central widget with tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Create tabs
        permissions = self.user.get('permissions', [])
        if self.user['role'] == 'admin' or 'Can access sales tab' in permissions:
            self.create_sales_tab()
        if self.user['role'] == 'admin' or 'Can access products tab' in permissions:
            self.create_products_tab()
        if self.user['role'] == 'admin' or 'Can access reports tab' in permissions:
            self.create_reports_tab()
        if self.user['role'] == 'admin' or 'Can access settings tab' in permissions:
            self.create_settings_tab()
        
        # Status bar
        self.status_bar = self.statusBar()
        self.update_status_bar()
        
        # Menu bar
        self.create_menu_bar()

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        QShortcut(QKeySequence("F2"), self, self.focus_search)
        QShortcut(QKeySequence("F3"), self, self.toggle_view_shortcut)
        QShortcut(QKeySequence("F5"), self, self.refresh_products_table)
        QShortcut(QKeySequence("Return"), self, self.add_to_cart_shortcut)
        QShortcut(QKeySequence("Enter"), self, self.add_to_cart_shortcut)

    def focus_search(self):
        self.search_input.setFocus()

    def toggle_view_shortcut(self):
        if self.products_stack.currentIndex() == 0:
            self.toggle_view('table')
        else:
            self.toggle_view('grid')

    def add_to_cart_shortcut(self):
        if self.products_stack.currentIndex() == 1: # Table view
            selected_items = self.products_table.selectedItems()
            if selected_items:
                row = selected_items[0].row()
                product = self.db.get_products_with_variants()[row]
                self.add_to_cart(product)

        # Keyboard shortcuts
        self.setup_shortcuts()
        
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        if self.user['role'] == 'admin':
            backup_action = QAction('Backup Database', self)
            backup_action.triggered.connect(self.backup_database)
            file_menu.addAction(backup_action)
        
        file_menu.addSeparator()
        
        logout_action = QAction('Logout', self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)
        
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Shift menu
        shift_menu = menubar.addMenu('Shift')
        
        close_shift_action = QAction('Close Shift', self)
        close_shift_action.triggered.connect(self.close_shift)
        shift_menu.addAction(close_shift_action)
        
    def create_sales_tab(self):
        """Create the main sales interface"""
        sales_widget = QWidget()
        layout = QHBoxLayout()
        
        # Left panel - Products
        left_panel = QVBoxLayout()
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products or scan barcode...")
        self.search_input.textChanged.connect(self.search_products)
        
        # View toggle buttons
        self.grid_view_btn = QPushButton("Grid View")
        self.table_view_btn = QPushButton("Table View")
        self.grid_view_btn.clicked.connect(lambda: self.toggle_view('grid'))
        self.table_view_btn.clicked.connect(lambda: self.toggle_view('table'))
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.grid_view_btn)
        search_layout.addWidget(self.table_view_btn)
        
        left_panel.addLayout(search_layout)
        
        # Products display (stacked widget for grid/table views)
        self.products_stack = QStackedWidget()
        
        # Grid view
        self.products_grid = QScrollArea()
        self.products_grid.setWidgetResizable(True)
        grid_widget = QWidget()
        self.grid_layout = QGridLayout(grid_widget)
        self.products_grid.setWidget(grid_widget)
        
        # Table view
        self.products_table = QTableWidget()
        columns = ['Product', 'Variant', 'Price', 'Stock', 'Action']
        self.products_table.setColumnCount(len(columns))
        self.products_table.setHorizontalHeaderLabels(columns)
        self.products_table.horizontalHeader().setStretchLastSection(True)
        
        self.products_stack.addWidget(self.products_grid)
        self.products_stack.addWidget(self.products_table)
        self.products_stack.setCurrentIndex(0)  # Start with grid view
        
        left_panel.addWidget(self.products_stack)
        
        # Right panel - Cart
        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("Shopping Cart"))
        
        # Cart table
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(['Item', 'Qty', 'Price', 'Total', 'Action'])
        self.cart_table.horizontalHeader().setStretchLastSection(True)
        right_panel.addWidget(self.cart_table)
        
        # Cart totals
        totals_layout = QVBoxLayout()
        
        self.subtotal_label = QLabel(f"Subtotal: {self.db.get_setting('currency_symbol')}0.00")
        self.tax_label = QLabel(f"Tax: {self.db.get_setting('currency_symbol')}0.00") 
        self.discount_label = QLabel(f"Discount: {self.db.get_setting('currency_symbol')}0.00")
        self.total_label = QLabel(f"Total: {self.db.get_setting('currency_symbol')}0.00")
        font = self.total_label.font()
        font.setBold(True)
        self.total_label.setFont(font)
        
        totals_layout.addWidget(self.subtotal_label)
        totals_layout.addWidget(self.tax_label)
        totals_layout.addWidget(self.discount_label)
        totals_layout.addWidget(self.total_label)
        
        right_panel.addLayout(totals_layout)
        
        # Payment buttons
        payment_layout = QGridLayout()

        self.cash_payment_btn = QPushButton("Cash")
        self.cash_payment_btn.clicked.connect(self.process_cash_payment)
        self.cash_payment_btn.setStyleSheet("background-color: #28a745;")

        self.card_payment_btn = QPushButton("Card")
        self.card_payment_btn.clicked.connect(lambda: self.process_other_payment("Card"))
        self.card_payment_btn.setStyleSheet("background-color: #17a2b8;")

        self.mpesa_payment_btn = QPushButton("M-Pesa")
        self.mpesa_payment_btn.clicked.connect(lambda: self.process_other_payment("Mpesa"))
        self.mpesa_payment_btn.setStyleSheet("background-color: #ffc107;")

        self.custom_item_btn = QPushButton("+ Custom Item")
        self.custom_item_btn.clicked.connect(self.add_custom_item)

        self.clear_cart_btn = QPushButton("Clear Cart")
        self.clear_cart_btn.clicked.connect(self.clear_cart)
        self.clear_cart_btn.setStyleSheet("background-color: #dc3545;")

        payment_layout.addWidget(self.cash_payment_btn, 0, 0)
        payment_layout.addWidget(self.card_payment_btn, 0, 1)
        payment_layout.addWidget(self.mpesa_payment_btn, 0, 2)

        self.split_payment_btn = QPushButton("Split Payment")
        self.split_payment_btn.clicked.connect(self.process_split_payment)
        self.split_payment_btn.setStyleSheet("background-color: #6c757d;")
        payment_layout.addWidget(self.split_payment_btn, 1, 0)

        payment_layout.addWidget(self.custom_item_btn, 1, 1)
        payment_layout.addWidget(self.clear_cart_btn, 1, 2)

        right_panel.addLayout(payment_layout)
        
        # Layout proportions
        layout.addLayout(left_panel, 2)
        layout.addLayout(right_panel, 1)
        
        sales_widget.setLayout(layout)
        self.tabs.addTab(sales_widget, "Sales")
        
        # Load products
        self.load_products()
        
    def create_products_tab(self):
        """Create products management tab"""
        products_widget = QWidget()
        layout = QVBoxLayout()
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        if self.user['role'] == 'admin':
            add_product_btn = QPushButton("Add Product")
            add_product_btn.clicked.connect(self.add_product_dialog)
            toolbar.addWidget(add_product_btn)
            
            add_supplier_btn = QPushButton("Add Supplier")
            add_supplier_btn.clicked.connect(self.show_add_supplier_dialog)
            toolbar.addWidget(add_supplier_btn)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_products_table)
        toolbar.addWidget(refresh_btn)
        
        toolbar.addStretch()
        
        # Low stock filter
        self.show_low_stock_cb = QCheckBox("Show Low Stock Only")
        self.show_low_stock_cb.toggled.connect(self.refresh_products_table)
        toolbar.addWidget(self.show_low_stock_cb)
        
        layout.addLayout(toolbar)
        
        # Products table
        self.products_mgmt_table = QTableWidget()
        self.products_mgmt_table.setColumnCount(11)
        headers = ['Product', 'Brand', 'Variant', 'Barcode', 'Purchase Price', 'Price', 'Stock', 'Reorder Level', 'Supplier', 'Status', 'Actions']
        self.products_mgmt_table.setHorizontalHeaderLabels(headers)
        self.products_mgmt_table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.products_mgmt_table)
        
        products_widget.setLayout(layout)
        self.tabs.addTab(products_widget, "Products")
        
        self.refresh_products_table()
        
    def create_summary_card(self, title, value, icon_path=None):
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setFrameShadow(QFrame.Raised)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #888;")
        
        value_label = QLabel(value)
        font = value_label.font()
        font.setBold(True)
        value_label.setFont(font)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        card.setLayout(layout)
        return card

    def create_reports_tab(self):
        """Create reports tab"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        reports_widget = QWidget()
        scroll_area.setWidget(reports_widget)
        layout = QVBoxLayout(reports_widget)

        # Header
        header_layout = QHBoxLayout()
        store_name = self.db.get_setting('store_name')
        header_label = QLabel(f"{store_name} Reports Dashboard")
        font = header_label.font()
        font.setBold(True)
        header_label.setFont(font)
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Date Range Selector
        date_range_layout = QHBoxLayout()
        date_range_layout.addWidget(QLabel("Date Range:"))
        self.today_rb = QRadioButton("Today")
        self.week_rb = QRadioButton("This Week")
        self.custom_rb = QRadioButton("Custom")
        self.from_date = QDateEdit()
        self.from_date.setDate(QDate.currentDate().addDays(-30))
        self.from_date.setCalendarPopup(True)
        self.to_date = QDateEdit()
        self.to_date.setDate(QDate.currentDate())
        self.to_date.setCalendarPopup(True)
        
        date_range_layout.addWidget(self.today_rb)
        date_range_layout.addWidget(self.week_rb)
        date_range_layout.addWidget(self.custom_rb)
        date_range_layout.addWidget(self.from_date)
        date_range_layout.addWidget(QLabel("To:"))
        date_range_layout.addWidget(self.to_date)
        date_range_layout.addStretch()
        layout.addLayout(date_range_layout)

        # Summary Cards
        summary_layout = QHBoxLayout()
        self.total_sales_card = self.create_summary_card("Total Sales", "$0.00")
        self.num_sales_card = self.create_summary_card("Number of Sales", "0")
        self.items_sold_card = self.create_summary_card("Items Sold", "0")
        self.profit_card = self.create_summary_card("Profit", "$0.00")
        summary_layout.addWidget(self.total_sales_card)
        summary_layout.addWidget(self.num_sales_card)
        summary_layout.addWidget(self.items_sold_card)
        summary_layout.addWidget(self.profit_card)
        layout.addLayout(summary_layout)

        # Charts
        charts_layout = QHBoxLayout()
        
        # Payment method chart
        self.payment_chart_widget = QWidget()
        self.payment_chart_layout = QVBoxLayout()
        self.payment_chart_widget.setLayout(self.payment_chart_layout)
        charts_layout.addWidget(self.payment_chart_widget)

        # Top products chart
        self.top_products_chart_widget = QWidget()
        self.top_products_chart_layout = QVBoxLayout()
        self.top_products_chart_widget.setLayout(self.top_products_chart_layout)
        charts_layout.addWidget(self.top_products_chart_widget)

        layout.addLayout(charts_layout)

        # Detailed Sales Table
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(7)
        self.sales_table.setHorizontalHeaderLabels(["Date", "Sale ID", "Customer", "Items", "Total", "Payment(s)", "Status"])
        layout.addWidget(self.sales_table)

        # Footer
        footer_layout = QHBoxLayout()
        download_btn = QPushButton("Download Report")
        print_btn = QPushButton("Print Report")
        footer_layout.addStretch()
        footer_layout.addWidget(download_btn)
        footer_layout.addWidget(print_btn)
        layout.addLayout(footer_layout)

        self.tabs.addTab(scroll_area, "Reports")

        # Connect signals
        self.today_rb.toggled.connect(self.update_reports)
        self.week_rb.toggled.connect(self.update_reports)
        self.custom_rb.toggled.connect(self.update_reports)
        self.from_date.dateChanged.connect(self.update_reports)
        self.to_date.dateChanged.connect(self.update_reports)

        self.update_reports()

    @property
    def currency_symbol(self):
        return self.db.get_setting('currency_symbol') or '$'

    def update_reports(self):
        start_date = self.from_date.date().toString("yyyy-MM-dd")
        end_date = self.to_date.date().toString("yyyy-MM-dd")

        if self.today_rb.isChecked():
            start_date = QDate.currentDate().toString("yyyy-MM-dd")
            end_date = QDate.currentDate().toString("yyyy-MM-dd")
        elif self.week_rb.isChecked():
            start_date = QDate.currentDate().addDays(-7).toString("yyyy-MM-dd")
            end_date = QDate.currentDate().toString("yyyy-MM-dd")

        # Update summary cards
        total_sales = self.db.get_total_sales(start_date, end_date)
        num_sales = self.db.get_number_of_sales(start_date, end_date)
        items_sold = self.db.get_items_sold(start_date, end_date)
        profit = self.db.get_profit(start_date, end_date)
        self.total_sales_card.findChildren(QLabel, None, Qt.FindChildrenRecursively)[1].setText(f"{self.currency_symbol}{total_sales:.2f}")
        self.num_sales_card.findChildren(QLabel, None, Qt.FindChildrenRecursively)[1].setText(str(num_sales))
        self.items_sold_card.findChildren(QLabel, None, Qt.FindChildrenRecursively)[1].setText(str(items_sold))
        self.profit_card.findChildren(QLabel, None, Qt.FindChildrenRecursively)[1].setText(f"{self.currency_symbol}{profit:.2f}")

        # Update payment method chart
        payment_data = self.db.get_sales_by_payment_method(start_date, end_date)
        self.update_payment_chart(payment_data)

        # Update top products chart
        top_products_data = self.db.get_top_products(start_date, end_date)
        self.update_top_products_chart(top_products_data)

        # Update detailed sales table
        detailed_sales = self.db.get_detailed_sales(start_date, end_date)
        self.sales_table.setRowCount(len(detailed_sales))
        for i, sale in enumerate(detailed_sales):
            self.sales_table.setItem(i, 0, QTableWidgetItem(sale['sale_date']))
            self.sales_table.setItem(i, 1, QTableWidgetItem(str(sale['sale_id'])))
            self.sales_table.setItem(i, 2, QTableWidgetItem("N/A")) # Customer name is not available
            self.sales_table.setItem(i, 3, QTableWidgetItem(str(self.db.get_items_sold_for_sale(sale['sale_id'])))) # Need a new db method for this
            self.sales_table.setItem(i, 4, QTableWidgetItem(f"{self.currency_symbol}{sale['total_amount']:.2f}"))
            self.sales_table.setItem(i, 5, QTableWidgetItem(sale['payments']))
            self.sales_table.setItem(i, 6, QTableWidgetItem(sale['status']))

    def update_payment_chart(self, data):
        for i in reversed(range(self.payment_chart_layout.count())):
            self.payment_chart_layout.itemAt(i).widget().setParent(None)

        if not data:
            self.payment_chart_layout.addWidget(QLabel("No payment data for this period."))
            return

        fig = Figure(figsize=(5, 4), dpi=100)
        canvas = FigureCanvas(fig)
        self.payment_chart_layout.addWidget(canvas)
        ax = fig.add_subplot(111)

        labels = [d['method'] for d in data]
        sizes = [d['total'] for d in data]
        
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        ax.set_title("Sales by Payment Method")

    def update_top_products_chart(self, data):
        for i in reversed(range(self.top_products_chart_layout.count())):
            self.top_products_chart_layout.itemAt(i).widget().setParent(None)

        if not data:
            self.top_products_chart_layout.addWidget(QLabel("No product data for this period."))
            return
            
        fig = Figure(figsize=(5, 4), dpi=100)
        canvas = FigureCanvas(fig)
        self.top_products_chart_layout.addWidget(canvas)
        ax = fig.add_subplot(111)

        product_names = [f"{d['product_name']} ({d['variant_name']})" for d in data]
        quantities = [d['total_qty'] for d in data]

        ax.bar(product_names, quantities)
        ax.set_title("Top Selling Products")
        ax.set_ylabel("Quantity Sold")
        fig.autofmt_xdate()
    def create_settings_tab(self):
        """Create settings tab (admin only)"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        settings_widget = QWidget()
        scroll_area.setWidget(settings_widget)
        layout = QVBoxLayout(settings_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Store Settings
        store_group = QGroupBox("Store Settings")
        store_layout = QFormLayout(store_group)
        store_layout.setSpacing(10)
        
        self.store_name_input = QLineEdit()
        self.store_address_input = QTextEdit()
        self.store_address_input.setMaximumHeight(80)
        self.currency_input = QLineEdit()
        self.tax_rate_input = QLineEdit()
        
        store_layout.addRow("Store Name:", self.store_name_input)
        store_layout.addRow("Store Address:", self.store_address_input)
        store_layout.addRow("Currency Symbol:", self.currency_input)
        store_layout.addRow("Tax Rate (%):", self.tax_rate_input)
        
        layout.addWidget(store_group)

        # Receipt Settings
        receipt_group = QGroupBox("Receipt Settings")
        receipt_layout = QFormLayout(receipt_group)
        receipt_layout.setSpacing(10)

        self.receipt_footer_input = QTextEdit()
        self.receipt_footer_input.setMaximumHeight(60)
        receipt_layout.addRow("Receipt Footer:", self.receipt_footer_input)

        layout.addWidget(receipt_group)

        # UI Settings
        ui_group = QGroupBox("UI Settings")
        ui_layout = QFormLayout(ui_group)
        ui_layout.setSpacing(10)

        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(["Small", "Medium", "Large"])
        ui_layout.addRow("Font Size:", self.font_size_combo)

        layout.addWidget(ui_group)
        
        # Save button
        save_settings_btn = QPushButton("Save Settings")
        save_settings_btn.clicked.connect(self.save_settings)
        save_settings_btn.setStyleSheet("min-width: 120px; padding: 10px;")
        layout.addWidget(save_settings_btn, 0, Qt.AlignRight)
        
        # User management section
        user_group = QGroupBox("User Management")
        users_layout = QVBoxLayout(user_group)
        
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(5)
        self.users_table.setHorizontalHeaderLabels(['ID', 'Username', 'Role', 'Created', 'Actions'])
        self.users_table.horizontalHeader().setStretchLastSection(True)
        self.users_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.users_table.setMinimumHeight(300)
        users_layout.addWidget(self.users_table)
        
        user_buttons = QHBoxLayout()
        add_user_btn = QPushButton("Add User")
        add_user_btn.clicked.connect(self.add_user_dialog)
        user_buttons.addWidget(add_user_btn)
        user_buttons.addStretch()
        
        users_layout.addLayout(user_buttons)
        layout.addWidget(user_group)
        
        layout.addStretch()
        
        self.tabs.addTab(scroll_area, "Settings")
        
        self.load_settings()
        self.load_users()
        
    def toggle_view(self, view_type):
        """Toggle between grid and table view"""
        if view_type == 'grid':
            self.products_stack.setCurrentIndex(0)
            self.grid_view_btn.setEnabled(False)
            self.table_view_btn.setEnabled(True)
        else:
            self.products_stack.setCurrentIndex(1)
            self.grid_view_btn.setEnabled(True)
            self.table_view_btn.setEnabled(False)
            
    def load_products(self, products=None):
        """Load products into both grid and table views"""
        if products is None:
            products = self.db.get_products_with_variants()
        
        # Clear existing items
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)
            
        self.products_table.setRowCount(0)
        self.products_table.setColumnCount(5)
        self.products_table.setHorizontalHeaderLabels(['Product', 'Variant', 'Price', 'Stock', 'Action'])
        
        # Populate grid view
        row, col = 0, 0
        for product in products:
            if product['variant_id'] is None:
                continue
                
            # Create product card
            card = QFrame()
            card.setFrameStyle(QFrame.Box)
            card.setFixedSize(200, 125)
            card.setStyleSheet("""
                QFrame {
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    background-color: white;
                    margin: 2px;
                }
                QFrame:hover {
                    border: 2px solid #007bff;
                }
            """)
            
            card_layout = QVBoxLayout()
            
            # Product name
            name_label = QLabel(f"{product['product_name']}")
            font = name_label.font()
            font.setBold(True)
            name_label.setFont(font)
            name_label.setWordWrap(True)
            card_layout.addWidget(name_label)
            
            # Variant and price (inclusive of tax)
            price_with_tax = self.get_price_with_tax(product['price'])
            variant_label = QLabel(f"{product['variant_name']} - {self.db.get_setting('currency_symbol')}{price_with_tax:.2f}")
            variant_label.setStyleSheet("color: #666;")
            card_layout.addWidget(variant_label)
            
            # Stock
            stock_color = "#28a745" if product['stock_quantity'] > product['reorder_level'] else "#ffc107" if product['stock_quantity'] > 0 else "#dc3545"
            stock_label = QLabel(f"Stock: {product['stock_quantity']}")
            stock_label.setStyleSheet(f"color: {stock_color};")
            card_layout.addWidget(stock_label)

            card_layout.addStretch() 
            
            # Add to cart button
            add_btn = QPushButton("Add to Cart")
            add_btn.setStyleSheet("padding: 4px;")
            add_btn.clicked.connect(lambda checked, p=product: self.add_to_cart(p))
            card_layout.addWidget(add_btn)
            
            card.setLayout(card_layout)
            self.grid_layout.addWidget(card, row, col)
            
            col += 1
            if col >= 4:  # 4 columns
                col = 0
                row += 1
                
        # Populate table view
        self.products_table.setRowCount(len([p for p in products if p['variant_id'] is not None]))
        row_idx = 0
        for product in products:
            if product['variant_id'] is None:
                continue
                
            price_with_tax = self.get_price_with_tax(product['price'])
            self.products_table.setItem(row_idx, 0, QTableWidgetItem(product['product_name']))
            self.products_table.setItem(row_idx, 1, QTableWidgetItem(product['variant_name'] or ''))
            self.products_table.setItem(row_idx, 2, QTableWidgetItem(f"{self.db.get_setting('currency_symbol')}{price_with_tax:.2f}"))
            self.products_table.setItem(row_idx, 3, QTableWidgetItem(str(product['stock_quantity'])))
            
            add_btn = QPushButton("Add")
            add_btn.clicked.connect(lambda checked, p=product: self.add_to_cart(p))
            self.products_table.setCellWidget(row_idx, 4, add_btn)
            
            row_idx += 1
            
    def search_products(self):
        """Search products and handle barcode input"""
        search_term = self.search_input.text().strip()
        
        if not search_term:
            self.load_products()
            return
            
        # Check if it might be a barcode (longer string, often numeric)
        if len(search_term) > 8 and search_term.replace('-', '').isdigit():
            # Try barcode lookup
            product = self.db.find_by_barcode(search_term)
            if product:
                # Auto-add to cart
                self.add_to_cart(product)
                self.search_input.clear()
                return
                
        # Regular search
        products = self.db.search_products(search_term)
        self.load_products(products)
        
    def add_to_cart(self, product):
        """Add product to cart"""
        if product['stock_quantity'] <= 0:
            QMessageBox.warning(self, "Out of Stock", "This item is out of stock!")
            return
            
        # Check if item already in cart
        for i, cart_item in enumerate(self.cart_items):
            if cart_item['variant_id'] == product['variant_id']:
                # Increase quantity
                if cart_item['qty'] < product['stock_quantity']:
                    self.cart_items[i]['qty'] += 1
                    self.cart_items[i]['total'] = self.cart_items[i]['qty'] * self.cart_items[i]['price']
                else:
                    QMessageBox.warning(self, "Stock Limit", "Cannot add more items than available in stock!")
                    return
                break
        else:
            # Add new item
            price = float(product['price'])
            # Price from DB is already tax-inclusive if TAX_INCLUSIVE is True
            cart_item = {
                'product_id': product['product_id'],
                'variant_id': product['variant_id'],
                'name': f"{product['product_name']} ({product['variant_name']})",
                'price': price,
                'qty': 1,
                'total': price
            }
            self.cart_items.append(cart_item)
            
        self.update_cart_display()
        self.search_input.setFocus()
        
    def update_cart_display(self):
        """Update cart table and totals"""
        self.cart_table.setRowCount(len(self.cart_items))
        self.cart_table.setColumnWidth(4, 50)
        
        subtotal = 0
        for i, item in enumerate(self.cart_items):
            self.cart_table.setItem(i, 0, QTableWidgetItem(item['name']))
            
            # Quantity spinbox
            qty_spin = QSpinBox()
            qty_spin.setMinimum(1)
            qty_spin.setValue(item['qty'])
            qty_spin.valueChanged.connect(lambda value, idx=i: self.update_cart_qty(idx, value))
            self.cart_table.setCellWidget(i, 1, qty_spin)
            
            self.cart_table.setItem(i, 2, QTableWidgetItem(f"{self.db.get_setting('currency_symbol')}{item['price']:.2f}"))
            self.cart_table.setItem(i, 3, QTableWidgetItem(f"{self.db.get_setting('currency_symbol')}{item['total']:.2f}"))
            
            # Remove button
            remove_btn = QPushButton("X")
            remove_btn.setStyleSheet("background-color: #dc3545;")
            remove_btn.clicked.connect(lambda checked, idx=i: self.remove_from_cart(idx))
            self.cart_table.setCellWidget(i, 4, remove_btn)
            
            subtotal += item['total']
            
        # Calculate totals
        tax_rate = float(self.db.get_setting('tax_rate') or '0') / 100
        
        if TAX_INCLUSIVE:
            total = subtotal
            subtotal_before_tax = total / (1 + tax_rate)
            tax_amount = total - subtotal_before_tax
            subtotal_display = subtotal_before_tax
        else:
            tax_amount = subtotal * tax_rate
            total = subtotal + tax_amount
            subtotal_display = subtotal
        
        # Update labels
        currency = self.db.get_setting('currency_symbol') or '$'
        self.subtotal_label.setText(f"Subtotal: {currency}{subtotal_display:.2f}")
        self.tax_label.setText(f"Tax: {currency}{tax_amount:.2f}")
        self.discount_label.setText(f"Discount: {currency}0.00")  # TODO: Implement discounts
        self.total_label.setText(f"Total: {currency}{total:.2f}")
        
    def update_cart_qty(self, index, qty):
        """Update cart item quantity"""
        self.cart_items[index]['qty'] = qty
        self.cart_items[index]['total'] = qty * self.cart_items[index]['price']
        self.update_cart_display()
        
    def remove_from_cart(self, index):
        """Remove item from cart"""
        del self.cart_items[index]
        self.update_cart_display()
        
    def clear_cart(self):
        """Clear all items from cart"""
        if self.cart_items:
            reply = QMessageBox.question(self, "Clear Cart", "Are you sure you want to clear the cart?")
            if reply == QMessageBox.Yes:
                self.cart_items.clear()
                self.update_cart_display()

    def add_custom_item(self):
        """Show dialog to add a custom item to the cart"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Custom Item")
        dialog.setFixedSize(300, 200)

        layout = QFormLayout()

        name_input = QLineEdit()
        price_input = QLineEdit()
        qty_input = QSpinBox()
        qty_input.setMinimum(1)

        layout.addRow("Item Name:", name_input)
        layout.addRow("Price:", price_input)
        layout.addRow("Quantity:", qty_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        def accept():
            try:
                price = float(price_input.text())
                qty = qty_input.value()
                if price > 0 and qty > 0:
                    item = {
                        'product_id': None,
                        'variant_id': None,
                        'name': name_input.text(),
                        'price': price,
                        'qty': qty,
                        'total': price * qty,
                        'stock_quantity': 9999 # Custom items have no stock limit
                    }
                    self.cart_items.append(item)
                    self.update_cart_display()
                    dialog.accept()
                else:
                    QMessageBox.warning(dialog, "Invalid Input", "Price and quantity must be greater than zero.")
            except ValueError:
                QMessageBox.warning(dialog, "Invalid Input", "Please enter a valid price.")

        buttons.accepted.connect(accept)
        buttons.rejected.connect(dialog.reject)

        layout.addRow(buttons)
        dialog.setLayout(layout)
        dialog.exec()
                
    def process_cash_payment(self):
        self.process_payment("Cash")

    def process_other_payment(self, method):
        self.process_payment(method)

    def process_payment(self, method):
        """Process payment"""
        if not self.cart_items:
            QMessageBox.warning(self, "Empty Cart", "Please add items to cart first!")
            return
            
        # Calculate total
        subtotal = sum(item['total'] for item in self.cart_items)
        tax_rate = float(self.db.get_setting('tax_rate') or '0') / 100
        
        if TAX_INCLUSIVE:
            total = subtotal
            tax_amount = total - (total / (1 + tax_rate))
        else:
            tax_amount = subtotal * tax_rate
            total = subtotal + tax_amount

        payments = []
        change = 0

        if method == "Cash":
            # Cash payment dialog
            cash_received, ok = QInputDialog.getDouble(
                self, "Cash Payment", f"Total: {self.db.get_setting('currency_symbol')}{total:.2f}\nEnter cash received:", 
                total, 0, 99999.99, 2
            )
            
            if not ok:
                return

            if cash_received < total:
                QMessageBox.warning(self, "Insufficient Cash", "Cash received is less than total amount!")
                return
            
            payments.append({'method': 'Cash', 'amount': total, 'reference': None})
            change = cash_received - total
        else:
            # For Card and M-Pesa, get an optional transaction reference
            reference, ok = QInputDialog.getText(self, f"{method} Payment", f"Enter {method} transaction reference (optional):")
            if not ok:
                return
            payments.append({'method': method, 'amount': total, 'reference': reference})

        # Process sale
        sale_id = self.db.create_sale(
            self.current_shift['id'], total, tax_amount, 0
        )
        
        # Add sale payments
        self.db.add_sale_payments(sale_id, payments)
        
        # Add sale items
        for item in self.cart_items:
            base_price = item['price']
            if TAX_INCLUSIVE:
                base_price = item['price'] / (1 + tax_rate)
            
            self.db.add_sale_item(
                sale_id, item.get('product_id'), item.get('variant_id'),
                item['qty'], base_price, item['qty'] * base_price
            )
            
        # Show change
        QMessageBox.information(
            self, "Payment Complete", 
            f"Payment successful!\nChange: {self.db.get_setting('currency_symbol')}{change:.2f}\n\nReceipt will be printed."
        )
        
        # Print receipt
        self.print_receipt(sale_id)
        
        # Clear cart
        self.cart_items.clear()
        self.update_cart_display()
        self.load_products()  # Refresh stock

    def process_split_payment(self):
        if not self.cart_items:
            QMessageBox.warning(self, "Empty Cart", "Please add items to cart first!")
            return

        subtotal = sum(item['total'] for item in self.cart_items)
        tax_rate = float(self.db.get_setting('tax_rate') or '0') / 100
        
        if TAX_INCLUSIVE:
            total = subtotal
            tax_amount = total - (total / (1 + tax_rate))
        else:
            tax_amount = subtotal * tax_rate
            total = subtotal + tax_amount

        dialog = SplitPaymentDialog(total, self)
        if dialog.exec() == QDialog.Accepted:
            payments = dialog.payments
            
            # Process sale
            sale_id = self.db.create_sale(
                self.current_shift['id'], total, tax_amount, 0
            )
            
            # Add sale payments
            self.db.add_sale_payments(sale_id, payments)

            # Add sale items
            for item in self.cart_items:
                base_price = item['price']
                if TAX_INCLUSIVE:
                    base_price = item['price'] / (1 + tax_rate)
                
                self.db.add_sale_item(
                    sale_id, item.get('product_id'), item.get('variant_id'),
                    item['qty'], base_price, item['qty'] * base_price
                )

            QMessageBox.information(self, "Payment Complete", "Payment successful!")
            
            self.print_receipt(sale_id)
            
            self.cart_items.clear()
            self.update_cart_display()
            self.load_products()
            
    def print_receipt(self, sale_id):
        """Print receipt for sale"""
        # TODO: Implement actual receipt printing
        sale_data = self.db.get_sale_with_items(sale_id)
        print(f"Printing receipt for sale #{sale_id}")
        
    def refresh_products_table(self):
        """Refresh products management table"""
        if self.show_low_stock_cb.isChecked():
            products = self.db.get_low_stock_items()
        else:
            products = self.db.get_products_with_variants()
            
        products = [p for p in products if p['variant_id'] is not None]
        
        self.products_mgmt_table.setRowCount(len(products))
        
        for i, product in enumerate(products):
            price_with_tax = self.get_price_with_tax(product['price'])
            self.products_mgmt_table.setItem(i, 0, QTableWidgetItem(product['product_name']))
            self.products_mgmt_table.setItem(i, 1, QTableWidgetItem(product.get('brand_name', '') or ''))
            self.products_mgmt_table.setItem(i, 2, QTableWidgetItem(product['variant_name'] or ''))
            self.products_mgmt_table.setItem(i, 3, QTableWidgetItem(product.get('variant_barcode', '') or ''))
            self.products_mgmt_table.setItem(i, 4, QTableWidgetItem(f"{self.db.get_setting('currency_symbol')}{product.get('purchase_price') or 0:.2f}"))
            self.products_mgmt_table.setItem(i, 5, QTableWidgetItem(f"{self.db.get_setting('currency_symbol')}{price_with_tax:.2f}"))
            self.products_mgmt_table.setItem(i, 6, QTableWidgetItem(str(product['stock_quantity'])))
            self.products_mgmt_table.setItem(i, 7, QTableWidgetItem(str(product['reorder_level'])))
            self.products_mgmt_table.setItem(i, 8, QTableWidgetItem(product.get('supplier_name', '') or ''))
            
            # Status
            if product['stock_quantity'] <= 0:
                status = "Out of Stock"
                color = "#dc3545"
            elif product['stock_quantity'] <= product['reorder_level']:
                status = "Low Stock"
                color = "#ffc107"
            else:
                status = "In Stock"
                color = "#28a745"
                
            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor(color))
            self.products_mgmt_table.setItem(i, 9, status_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            if product.get('supplier_name'):
                reorder_btn = QPushButton("Re-order")
                reorder_btn.setStyleSheet("background-color: #ffc107; color: black;")
                reorder_btn.clicked.connect(lambda checked, p=product: self.show_reorder_info(p))
                actions_layout.addWidget(reorder_btn)
                
            if self.user['role'] == 'admin':
                edit_btn = QPushButton("Edit")
                edit_btn.clicked.connect(lambda checked, p=product: self.edit_product(p))
                actions_layout.addWidget(edit_btn)
                
            actions_widget.setLayout(actions_layout)
            self.products_mgmt_table.setCellWidget(i, 10, actions_widget)
            
    def show_reorder_info(self, product):
        """Show supplier reorder information"""
        msg = QMessageBox()
        msg.setWindowTitle("Re-order Information")
        msg.setIcon(QMessageBox.Information)
        
        info_text = f"""
        Product: {product['product_name']} ({product['variant_name']})
        Current Stock: {product['stock_quantity']}
        Reorder Level: {product['reorder_level']}
        
        Supplier Information:
        Name: {product.get('supplier_name', 'N/A')}
        Phone: {product.get('supplier_phone', 'N/A')}
        Email: {product.get('supplier_email', 'N/A')}
        
        Please contact the supplier to reorder this item.
        """
        
        msg.setText(info_text)
        msg.exec()
        
    def generate_report(self):
        """Generate sales report"""
        start_date = self.from_date.date().toString("yyyy-MM-dd")
        end_date = self.to_date.date().toString("yyyy-MM-dd")
        
        summary = self.db.get_sales_summary(start_date, end_date)
        
        report_text = f"""
SALES REPORT
From: {start_date} To: {end_date}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY
-------
Total Sales: {summary['summary']['total_sales'] or 0}
Total Revenue: ${summary['summary']['total_revenue'] or 0:.2f}
Total Tax: ${summary['summary']['total_tax'] or 0:.2f}
Total Discounts: ${summary['summary']['total_discounts'] or 0:.2f}

REVENUE BY PAYMENT METHOD
-------------------------
"""
        for pm in summary['payment_methods']:
            report_text += f"{pm['method']}: ${pm['total']:.2f}\n"

        report_text += "\nTOP PRODUCTS\n------------\n"
        
        for product in summary['top_products'][:10]:
            report_text += f"{product['product_name']} ({product['variant_name']}): {product['total_qty']} units - {self.db.get_setting('currency_symbol')}{product['total_revenue']:.2f}\n"
            
        self.report_text.setText(report_text)
        
    def export_report_csv(self):
        """Export report to CSV"""
        # TODO: Implement CSV export
        QMessageBox.information(self, "Export", "CSV export functionality will be implemented here.")
        
    def load_settings(self):
        """Load settings into form"""
        settings = self.db.get_all_settings()
        
        self.store_name_input.setText(settings.get('store_name', ''))
        self.store_address_input.setText(settings.get('store_address', ''))
        self.currency_input.setText(settings.get('currency_symbol', '$'))
        self.tax_rate_input.setText(settings.get('tax_rate', '0'))
        self.receipt_footer_input.setText(settings.get('receipt_footer', ''))

        font_size = settings.get('font_size', 'Medium')
        index = self.font_size_combo.findText(font_size)
        if index != -1:
            self.font_size_combo.setCurrentIndex(index)
        self.set_font_size(font_size)

    def set_font_size(self, size_str):
        """Set application font size"""
        if size_str == 'Small':
            font_size = 10
        elif size_str == 'Large':
            font_size = 14
        else: # Medium
            font_size = 12
        
        font = self.app.font()
        font.setPointSize(font_size)
        self.app.setFont(font)
        
    def save_settings(self):
        """Save settings"""
        self.db.set_setting('store_name', self.store_name_input.text())
        self.db.set_setting('store_address', self.store_address_input.toPlainText())
        self.db.set_setting('currency_symbol', self.currency_input.text())
        self.db.set_setting('tax_rate', self.tax_rate_input.text())
        self.db.set_setting('receipt_footer', self.receipt_footer_input.toPlainText())
        
        font_size_str = self.font_size_combo.currentText()
        self.db.set_setting('font_size', font_size_str)
        self.set_font_size(font_size_str)
        
        QMessageBox.information(self, "Settings", "Settings saved successfully!")
        
    def load_users(self):
        """Load users into table"""
        users = self.db.get_all_users()
        
        self.users_table.setRowCount(len(users))
        for i, user in enumerate(users):
            self.users_table.setItem(i, 0, QTableWidgetItem(str(user['id'])))
            self.users_table.setItem(i, 1, QTableWidgetItem(user['username']))
            self.users_table.setItem(i, 2, QTableWidgetItem(user['role'].title()))
            self.users_table.setItem(i, 3, QTableWidgetItem(user['created_at'][:10]))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)

            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, u=user: self.edit_user_dialog(u))
            actions_layout.addWidget(edit_btn)

            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("background-color: #dc3545;")
            delete_btn.clicked.connect(lambda checked, u=user: self.delete_user(u))
            actions_layout.addWidget(delete_btn)

            actions_widget.setLayout(actions_layout)
            self.users_table.setCellWidget(i, 4, actions_widget)

    def edit_user_dialog(self, user):
        """Show edit user dialog"""
        dialog = EditUserDialog(self.db, user, self)
        if dialog.exec() == QDialog.Accepted:
            self.load_users()

    def delete_user(self, user):
        """Delete a user"""
        reply = QMessageBox.question(self, "Delete User", f"Are you sure you want to delete the user '{user['username']}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            if self.db.delete_user(user['id']):
                QMessageBox.information(self, "Success", "User deleted successfully!")
                self.load_users()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete user.")
            
    def add_user_dialog(self):
        """Show add user dialog"""
        dialog = AddUserDialog(self.db, self)
        if dialog.exec() == QDialog.Accepted:
            self.load_users()
        
    def add_product_dialog(self):
        """Show add product dialog with variant support"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Product")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # Product Details
        details_group = QGroupBox("Product Details")
        form_layout = QFormLayout()
        
        # Product Name
        self.product_name_input = QLineEdit()
        form_layout.addRow("Product Name*:", self.product_name_input)
        
        # Category with Add button
        category_layout = QHBoxLayout()
        self.category_combo = QComboBox()
        self.category_combo.setMinimumWidth(200)
        self.load_categories()
        
        add_category_btn = QPushButton("+")
        add_category_btn.setFixedWidth(30)
        add_category_btn.setToolTip("Add new category")
        add_category_btn.clicked.connect(self.show_add_category_dialog)
        
        category_layout.addWidget(self.category_combo)
        category_layout.addWidget(add_category_btn)
        form_layout.addRow("Category:", category_layout)
        
        # Brand with Add button
        brand_layout = QHBoxLayout()
        self.brand_combo = QComboBox()
        self.brand_combo.setMinimumWidth(200)
        self.load_brands()
        
        add_brand_btn = QPushButton("+")
        add_brand_btn.setFixedWidth(30)
        add_brand_btn.setToolTip("Add new brand")
        add_brand_btn.clicked.connect(self.show_add_brand_dialog)
        
        brand_layout.addWidget(self.brand_combo)
        brand_layout.addWidget(add_brand_btn)
        form_layout.addRow("Brand:", brand_layout)
        
        # Supplier
        supplier_layout = QHBoxLayout()
        self.supplier_combo = QComboBox()
        self.supplier_combo.setMinimumWidth(300)
        self.suppliers = self.db.get_all_suppliers()
        self.supplier_combo.addItem("Select Supplier", None)
        for supplier in self.suppliers:
            self.supplier_combo.addItem(supplier['name'], supplier['id'])
            
        add_supplier_btn = QPushButton("New Supplier")
        add_supplier_btn.clicked.connect(self.show_add_supplier_dialog)
        
        supplier_layout.addWidget(self.supplier_combo)
        supplier_layout.addWidget(add_supplier_btn)
        form_layout.addRow("Supplier:", supplier_layout)
        
        # Removed description field as per requirements
        
        # Variants
        self.variants_table = QTableWidget()
        self.variants_table.setColumnCount(6)
        self.variants_table.setHorizontalHeaderLabels(["Variant Name", "Barcode", "Purchase Price", "Selling Price", "Stock", "Reorder Level"])
        self.variants_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Add a default variant row
        self.add_variant_row()
        
        # Buttons for variants
        variant_buttons = QHBoxLayout()
        add_variant_btn = QPushButton("Add Variant")
        add_variant_btn.clicked.connect(self.add_variant_row)
        remove_variant_btn = QPushButton("Remove Selected")
        remove_variant_btn.clicked.connect(self.remove_selected_variant)
        variant_buttons.addWidget(add_variant_btn)
        variant_buttons.addWidget(remove_variant_btn)
        
        form_layout.addRow("Variants:", QLabel(""))
        form_layout.addRow(self.variants_table)
        form_layout.addRow(variant_buttons)
        
        details_group.setLayout(form_layout)
        layout.addWidget(details_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.save_product(dialog))
        button_box.rejected.connect(dialog.reject)
        
        layout.addWidget(button_box)
        dialog.setLayout(layout)
        dialog.exec()
        
    def add_variant_row(self, variant_name="", barcode="", purchase_price=0, price=0, stock=0, reorder_level=5, variant_id=None):
        """Add a new variant row to the variants table"""
        row = self.variants_table.rowCount()
        self.variants_table.insertRow(row)
        
        # Variant name
        name_item = QTableWidgetItem(variant_name)
        if variant_id:
            name_item.setData(Qt.UserRole, variant_id)
        self.variants_table.setItem(row, 0, name_item)

        # Barcode
        barcode_item = QTableWidgetItem(barcode)
        self.variants_table.setItem(row, 1, barcode_item)
        
        # Purchase Price
        purchase_price_item = QTableWidgetItem(f"{purchase_price or 0:.2f}")
        purchase_price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.variants_table.setItem(row, 2, purchase_price_item)

        # Selling Price
        price_item = QTableWidgetItem(f"{price:.2f}")
        price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.variants_table.setItem(row, 3, price_item)
        
        # Stock
        stock_item = QTableWidgetItem(str(stock))
        stock_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.variants_table.setItem(row, 4, stock_item)
        
        # Reorder Level
        reorder_item = QTableWidgetItem(str(reorder_level))
        reorder_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.variants_table.setItem(row, 5, reorder_item)
        
        # Select the new row
        self.variants_table.selectRow(row)
        
    def load_categories(self):
        """Load categories into the combo box"""
        self.category_combo.clear()
        self.category_combo.addItem("Select Category", None)
        categories = self.db.get_all_categories()
        for cat in categories:
            self.category_combo.addItem(cat['name'], cat['id'])
            
    def load_brands(self):
        """Load brands into the combo box"""
        self.brand_combo.clear()
        self.brand_combo.addItem("Select Brand", None)
        brands = self.db.get_all_brands()
        for brand in brands:
            self.brand_combo.addItem(brand['name'], brand['id'])
            
    def show_add_category_dialog(self):
        """Show dialog to add a new category"""
        name, ok = QInputDialog.getText(
            self, "Add Category", "Category Name:", 
            QLineEdit.Normal, ""
        )
        
        if ok and name.strip():
            try:
                category_id = self.db.add_category(name=name.strip())
                self.load_categories()
                # Select the newly added category
                index = self.category_combo.findData(category_id)
                if index >= 0:
                    self.category_combo.setCurrentIndex(index)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add category: {str(e)}")
    
    def show_add_brand_dialog(self):
        """Show dialog to add a new brand"""
        name, ok = QInputDialog.getText(
            self, "Add Brand", "Brand Name:", 
            QLineEdit.Normal, ""
        )
        
        if ok and name.strip():
            try:
                brand_id = self.db.add_brand(name=name.strip())
                self.load_brands()
                # Select the newly added brand
                index = self.brand_combo.findData(brand_id)
                if index >= 0:
                    self.brand_combo.setCurrentIndex(index)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add brand: {str(e)}")
    
    def remove_selected_variant(self):
        """Remove selected variant row"""
        selected = self.variants_table.selectionModel().selectedRows()
        for idx in sorted(selected, reverse=True):
            self.variants_table.removeRow(idx.row())
            
    def save_product(self, dialog):
        """Save the product and its variants"""
        # Validate inputs
        product_name = self.product_name_input.text().strip()
        if not product_name:
            QMessageBox.warning(self, "Validation Error", "Product name is required!")
            return
            
        # Check if at least one variant exists
        if self.variants_table.rowCount() == 0:
            QMessageBox.warning(self, "Validation Error", "At least one variant is required!")
            return
            
        # Validate variants
        variants = []
        for row in range(self.variants_table.rowCount()):
            variant_name = self.variants_table.item(row, 0).text().strip()
            barcode = self.variants_table.item(row, 1).text().strip()
            purchase_price = self.variants_table.item(row, 2).text().strip()
            price = self.variants_table.item(row, 3).text().strip()
            stock = self.variants_table.item(row, 4).text().strip()
            reorder_level = self.variants_table.item(row, 5).text().strip()
            
            if not variant_name:
                QMessageBox.warning(self, "Validation Error", f"Variant name is required for row {row + 1}")
                return

            if barcode and self.db.find_by_barcode(barcode):
                QMessageBox.warning(self, "Validation Error", f"Barcode {barcode} already exists.")
                return
                
            try:
                purchase_price = float(purchase_price)
                price = float(price)
                stock = int(stock)
                reorder_level = int(reorder_level)
                if price < 0 or stock < 0 or reorder_level < 0 or purchase_price < 0:
                    raise ValueError("Negative values not allowed")
            except (ValueError, AttributeError):
                QMessageBox.warning(self, "Validation Error", 
                                  f"Invalid price, stock or reorder level value in row {row + 1}")
                return
                
            variants.append({
                'name': variant_name,
                'barcode': barcode,
                'purchase_price': purchase_price,
                'price': price,
                'stock': stock,
                'reorder_level': reorder_level
            })
        
        # Get other product details
        category_id = self.category_combo.currentData()
        brand_id = self.brand_combo.currentData()
        supplier_id = self.supplier_combo.currentData()
        
        # Start transaction
        try:
            # Save product
            product_id = self.db.add_product(
                name=product_name,
                category_id=category_id,
                brand_id=brand_id,
                supplier_id=supplier_id
            )
            
            # Save variants
            for variant in variants:
                self.db.add_product_variant(
                    product_id=product_id,
                    name=variant['name'],
                    barcode=variant['barcode'],
                    purchase_price=variant['purchase_price'],
                    price=variant['price'],
                    stock_quantity=variant['stock'],
                    reorder_level=variant['reorder_level']
                )
                
            QMessageBox.information(self, "Success", "Product added successfully!")
            dialog.accept()
            self.refresh_products_table()
            self.load_products()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save product: {str(e)}")
        
    def show_add_supplier_dialog(self):
        """Show dialog to add a new supplier"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Supplier")
        dialog.setMinimumWidth(400)
        
        layout = QFormLayout()
        
        # Supplier fields
        name_input = QLineEdit()
        email_input = QLineEdit()
        phone_input = QLineEdit()
        address_input = QTextEdit()
        address_input.setMaximumHeight(60)
        
        layout.addRow("Supplier Name*:", name_input)
        layout.addRow("Email:", email_input)
        layout.addRow("Phone:", phone_input)
        layout.addRow("Address:", address_input)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        
        def save_supplier():
            name = name_input.text().strip()
            if not name:
                QMessageBox.warning(dialog, "Validation Error", "Supplier name is required!")
                return
                
            try:
                supplier_id = self.db.add_supplier(
                    name=name,
                    email=email_input.text().strip() or None,
                    phone=phone_input.text().strip() or None,
                    address=address_input.toPlainText().strip() or None
                )
                
                # Update the supplier combo
                self.suppliers = self.db.get_all_suppliers()
                self.supplier_combo.clear()
                self.supplier_combo.addItem("Select Supplier", None)
                for supplier in self.suppliers:
                    self.supplier_combo.addItem(supplier['name'], supplier['id'])
                    if supplier['id'] == supplier_id:
                        self.supplier_combo.setCurrentIndex(self.supplier_combo.count() - 1)
                
                dialog.accept()
                QMessageBox.information(self, "Success", "Supplier added successfully!")
                
            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Failed to add supplier: {str(e)}")
        
        button_box.accepted.connect(save_supplier)
        button_box.rejected.connect(dialog.reject)
        
        layout.addRow(button_box)
        dialog.setLayout(layout)
        dialog.exec()
        
    def edit_product(self, product):
        """Edit product"""
        product_id = product["product_id"]
        full_product = self.db.get_product_with_variants_by_id(product_id)
        self.edit_product_dialog(full_product)

    def edit_product_dialog(self, product):
        """Show edit product dialog with variant support"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Product")
        dialog.setMinimumWidth(500)

        layout = QVBoxLayout()

        # Product Details
        details_group = QGroupBox("Product Details")
        form_layout = QFormLayout()

        # Product Name
        self.product_name_input = QLineEdit(product['product_name'])
        form_layout.addRow("Product Name*:", self.product_name_input)

        # Category with Add button
        category_layout = QHBoxLayout()
        self.category_combo = QComboBox()
        self.category_combo.setMinimumWidth(200)
        self.load_categories()
        if product.get('category_id'):
            index = self.category_combo.findData(product['category_id'])
            if index >= 0:
                self.category_combo.setCurrentIndex(index)

        add_category_btn = QPushButton("+")
        add_category_btn.setFixedWidth(30)
        add_category_btn.setToolTip("Add new category")
        add_category_btn.clicked.connect(self.show_add_category_dialog)

        category_layout.addWidget(self.category_combo)
        category_layout.addWidget(add_category_btn)
        form_layout.addRow("Category:", category_layout)

        # Brand with Add button
        brand_layout = QHBoxLayout()
        self.brand_combo = QComboBox()
        self.brand_combo.setMinimumWidth(200)
        self.load_brands()
        if product.get('brand_id'):
            index = self.brand_combo.findData(product['brand_id'])
            if index >= 0:
                self.brand_combo.setCurrentIndex(index)

        add_brand_btn = QPushButton("+")
        add_brand_btn.setFixedWidth(30)
        add_brand_btn.setToolTip("Add new brand")
        add_brand_btn.clicked.connect(self.show_add_brand_dialog)

        brand_layout.addWidget(self.brand_combo)
        brand_layout.addWidget(add_brand_btn)
        form_layout.addRow("Brand:", brand_layout)

        # Supplier
        supplier_layout = QHBoxLayout()
        self.supplier_combo = QComboBox()
        self.supplier_combo.setMinimumWidth(300)
        self.suppliers = self.db.get_all_suppliers()
        self.supplier_combo.addItem("Select Supplier", None)
        for supplier in self.suppliers:
            self.supplier_combo.addItem(supplier['name'], supplier['id'])
        if product.get('supplier_id'):
            index = self.supplier_combo.findData(product['supplier_id'])
            if index >= 0:
                self.supplier_combo.setCurrentIndex(index)

        add_supplier_btn = QPushButton("New Supplier")
        add_supplier_btn.clicked.connect(self.show_add_supplier_dialog)

        supplier_layout.addWidget(self.supplier_combo)
        supplier_layout.addWidget(add_supplier_btn)
        form_layout.addRow("Supplier:", supplier_layout)

        # Variants
        self.variants_table = QTableWidget()
        self.variants_table.setColumnCount(6)
        self.variants_table.setHorizontalHeaderLabels(["Variant Name", "Barcode", "Purchase Price", "Selling Price", "Stock", "Reorder Level"])
        self.variants_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        variants = self.db.get_variants_for_product(product['product_id'])
        for variant in variants:
            self.add_variant_row(variant['name'], variant.get('barcode', ''), variant.get('purchase_price', 0), variant['price'], variant['stock_quantity'], variant['reorder_level'], variant['id'])

        # Buttons for variants
        variant_buttons = QHBoxLayout()
        add_variant_btn = QPushButton("Add Variant")
        add_variant_btn.clicked.connect(self.add_variant_row)
        remove_variant_btn = QPushButton("Remove Selected")
        remove_variant_btn.clicked.connect(self.remove_selected_variant)
        variant_buttons.addWidget(add_variant_btn)
        variant_buttons.addWidget(remove_variant_btn)

        form_layout.addRow("Variants:", QLabel(""))
        form_layout.addRow(self.variants_table)
        form_layout.addRow(variant_buttons)

        details_group.setLayout(form_layout)
        layout.addWidget(details_group)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.save_edited_product(dialog, product['product_id']))
        button_box.rejected.connect(dialog.reject)

        layout.addWidget(button_box)
        dialog.setLayout(layout)
        dialog.exec()

    def save_edited_product(self, dialog, product_id):
        """Save the edited product and its variants"""
        # Validate inputs
        product_name = self.product_name_input.text().strip()
        if not product_name:
            QMessageBox.warning(self, "Validation Error", "Product name is required!")
            return

        # Check if at least one variant exists
        if self.variants_table.rowCount() == 0:
            QMessageBox.warning(self, "Validation Error", "At least one variant is required!")
            return

        # Validate variants
        variants = []
        for row in range(self.variants_table.rowCount()):
            variant_id = self.variants_table.item(row, 0).data(Qt.UserRole)
            variant_name = self.variants_table.item(row, 0).text().strip()
            barcode = self.variants_table.item(row, 1).text().strip()
            purchase_price = self.variants_table.item(row, 2).text().strip()
            price = self.variants_table.item(row, 3).text().strip()
            stock = self.variants_table.item(row, 4).text().strip()
            reorder_level = self.variants_table.item(row, 5).text().strip()

            if not variant_name:
                QMessageBox.warning(self, "Validation Error", f"Variant name is required for row {row + 1}")
                return

            if barcode:
                existing_variant = self.db.find_by_barcode(barcode)
                if existing_variant and existing_variant['id'] != variant_id:
                    QMessageBox.warning(self, "Validation Error", f"Barcode {barcode} already exists.")
                    return

            try:
                purchase_price = float(purchase_price)
                price = float(price)
                stock = int(stock)
                reorder_level = int(reorder_level)
                if price < 0 or stock < 0 or reorder_level < 0 or purchase_price < 0:
                    raise ValueError("Negative values not allowed")
            except (ValueError, AttributeError):
                QMessageBox.warning(self, "Validation Error",
                                  f"Invalid price, stock or reorder level value in row {row + 1}")
                return

            variants.append({
                'id': variant_id,
                'name': variant_name,
                'barcode': barcode,
                'purchase_price': purchase_price,
                'price': price,
                'stock': stock,
                'reorder_level': reorder_level
            })

        # Get other product details
        category_id = self.category_combo.currentData()
        brand_id = self.brand_combo.currentData()
        supplier_id = self.supplier_combo.currentData()

        # Start transaction
        try:
            # Save product
            self.db.update_product(
                product_id=product_id,
                name=product_name,
                category_id=category_id,
                brand_id=brand_id,
                supplier_id=supplier_id,
                variants=variants
            )

            QMessageBox.information(self, "Success", "Product updated successfully!")
            dialog.accept()
            self.refresh_products_table()
            self.load_products()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save product: {str(e)}")
        
    def backup_database(self):
        """Backup database"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Backup Database", f"pos_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
            "Database Files (*.db)"
        )
        
        if filename:
            import shutil
            try:
                shutil.copy2(self.db.db_path, filename)
                QMessageBox.information(self, "Backup", "Database backed up successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Backup Error", f"Failed to backup database: {str(e)}")
                
    def close_shift(self):
        """Close current shift"""
        if not self.current_shift:
            return
            
        closing_cash, ok = QInputDialog.getDouble(
            self, "Close Shift", "Enter actual cash amount in drawer:", 
            0, 0, 99999.99, 2
        )
        
        if ok:
            self.db.close_shift(self.current_shift['id'], closing_cash)
            
            # Show EOD report
            shift_data = dict(self.current_shift)
            shift_data['closing_cash'] = closing_cash
            
            eod_dialog = EndOfDayDialog(self.db, shift_data, self)
            eod_dialog.exec()
            
            # Restart shift
            self.current_shift = None
            self.check_shift()
            
    def logout(self):
        """Logout current user and return to login screen"""
        reply = QMessageBox.question(self, "Logout", "Are you sure you want to logout?")
        if reply == QMessageBox.Yes:
            # Set flag to indicate logout was requested
            self.should_logout = True
            # Close the current window
            self.close()
            
    def get_price_with_tax(self, price: float) -> float:
        """
        If prices are tax-inclusive, returns the price as is.
        If prices are tax-exclusive, calculates and returns the price with tax.
        """
        if TAX_INCLUSIVE:
            return price
        
        try:
            tax_rate = float(self.db.get_setting('tax_rate') or '0') / 100
            return price * (1 + tax_rate)
        except (ValueError, TypeError):
            return price
            
    def update_status_bar(self):
        """Update status bar with current info"""
        if self.current_shift:
            shift_start = self.current_shift['start_time'][:16].replace('T', ' ')
            status_text = f"User: {self.user['username']} | Shift Started: {shift_start} | Opening Cash: {self.db.get_setting('currency_symbol')}{self.current_shift['opening_cash']:.2f}"
            self.status_bar.showMessage(status_text)


class POSApplication:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.db = POSDatabase()
        self.db.init_database()
        
        # Set application properties
        self.app.setApplicationName("POS System")
        self.app.setApplicationVersion("1.0")
        self.app.setOrganizationName("Your Store")
        
        # Apply application-wide styles
        self.app.setStyleSheet("""
            QApplication {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11px;
            }
        """)
        
    def run(self):
        """Run the application"""
        if not user_auth.check_syscfg_exists():
            reply = QMessageBox.question(None, "First-Time Setup", 
                                           "This application is not activated. Do you want to perform first-time setup?",
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                if not self.perform_first_time_setup():
                    return -1 # Exit if setup fails
            else:
                return -1 # Exit if user declines setup

        while True:
            # Show login dialog
            login_dialog = LoginDialog(self.db)
            if login_dialog.exec() != QDialog.Accepted:
                break
                
            # Create main window
            main_window = POSMainWindow(self.app, self.db, login_dialog.user)
            main_window.show()
            
            # Run event loop
            self.app.exec()
            
            # Check if we should continue (logout vs exit)
            if not hasattr(main_window, 'should_logout') or not main_window.should_logout:
                break
                
        return 0

    def perform_first_time_setup(self):
        """Handles the entire first-time setup and activation process."""
        # 1. Get user info
        setup_dialog = FirstTimeSetupDialog()
        if setup_dialog.exec() != QDialog.Accepted:
            return False

        name, phone_number = setup_dialog.get_data()
        if not name or not phone_number:
            QMessageBox.critical(None, "Error", "Name and phone number are required.")
            return False

        # 2. Request OTP
        response = user_auth.send_activation_request(name, phone_number)
        if not response.get("success"):
            QMessageBox.critical(None, "Error", response.get("message", "Failed to send activation request."))
            return False
        
        QMessageBox.information(None, "OTP Sent", "An OTP has been sent to your phone number.")

        # 3. Verify OTP
        verify_dialog = VerifyOTPDialog(phone_number)
        if verify_dialog.exec() != QDialog.Accepted:
            return False

        otp = verify_dialog.get_otp()
        if not otp:
            QMessageBox.critical(None, "Error", "OTP is required.")
            return False

        verify_response = user_auth.verify_otp(phone_number, otp)
        if not verify_response.get("success"):
            QMessageBox.critical(None, "Error", verify_response.get("message", "OTP verification failed."))
            return False
            
        QMessageBox.information(None, "Success", "OTP verified successfully!")

        # 4. Create user
        create_user_dialog = CreateUserDialog()
        if create_user_dialog.exec() != QDialog.Accepted:
            return False

        username, password = create_user_dialog.get_credentials()
        if not username or not password:
            QMessageBox.critical(None, "Error", "Username and password are required.")
            return False

        if not self.db.create_user(username, password, "admin", ["Can access sales tab", "Can access products tab", "Can access reports tab", "Can access settings tab"]):
            QMessageBox.critical(None, "Error", "Failed to create user. Username might already exist.")
            return False
            
        QMessageBox.information(None, "User Created", "Administrator user created successfully.")

        # 5. Write syscfg file
        machine_fingerprint = user_auth.get_machine_fingerprint()
        user_auth.write_syscfg_file(phone_number, machine_fingerprint)
        
        QMessageBox.information(None, "Activation Complete", "Application activated successfully! Please login.")

        return True


if __name__ == '__main__':
    app = POSApplication()
    sys.exit(app.run())
