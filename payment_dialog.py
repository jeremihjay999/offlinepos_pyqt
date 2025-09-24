from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from decimal import Decimal, InvalidOperation

class SplitPaymentDialog(QDialog):
    def __init__(self, total_amount, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Split Payment")
        self.total_amount = Decimal(total_amount)
        self.payments = []

        self.init_ui()
        self.update_totals()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setMinimumWidth(500)

        # Totals display
        totals_layout = QHBoxLayout()
        self.total_label = QLabel(f"Total: {self.total_amount:.2f}")
        self.paid_label = QLabel("Paid: 0.00")
        self.remaining_label = QLabel(f"Remaining: {self.total_amount:.2f}")
        totals_layout.addWidget(self.total_label)
        totals_layout.addWidget(self.paid_label)
        totals_layout.addWidget(self.remaining_label)
        layout.addLayout(totals_layout)

        # Payment entry
        entry_layout = QFormLayout()
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Cash", "Card", "Mpesa", "Bank"])
        self.amount_input = QLineEdit()
        self.amount_input.setValidator(QDoubleValidator(0.00, 99999.99, 2))
        self.reference_input = QLineEdit()
        self.reference_input.setPlaceholderText("Optional transaction reference")
        add_payment_btn = QPushButton("Add Payment")
        add_payment_btn.clicked.connect(self.add_payment)

        entry_layout.addRow("Method:", self.method_combo)
        entry_layout.addRow("Amount:", self.amount_input)
        entry_layout.addRow("Reference:", self.reference_input)
        entry_layout.addRow(add_payment_btn)
        layout.addLayout(entry_layout)

        # Payments table
        self.payments_table = QTableWidget()
        self.payments_table.setColumnCount(4)
        self.payments_table.setHorizontalHeaderLabels(["Method", "Amount", "Reference", "Action"])
        layout.addWidget(self.payments_table)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.ok_button = button_box.button(QDialogButtonBox.Ok)
        self.ok_button.setText("Complete Sale")
        self.ok_button.setEnabled(False)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def add_payment(self):
        method = self.method_combo.currentText()
        amount_str = self.amount_input.text()
        reference = self.reference_input.text().strip()

        try:
            amount = Decimal(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except (ValueError, InvalidOperation):
            QMessageBox.warning(self, "Invalid Amount", "Please enter a valid positive amount.")
            return

        paid_amount = sum(p['amount'] for p in self.payments)
        if amount > self.total_amount - paid_amount:
            QMessageBox.warning(self, "Amount Exceeds Balance", "The payment amount cannot exceed the remaining balance.")
            return

        payment = {"method": method, "amount": amount, "reference": reference}
        self.payments.append(payment)
        self.update_payments_table()
        self.update_totals()
        self.amount_input.clear()
        self.reference_input.clear()

    def update_payments_table(self):
        self.payments_table.setRowCount(len(self.payments))
        for i, payment in enumerate(self.payments):
            self.payments_table.setItem(i, 0, QTableWidgetItem(payment['method']))
            self.payments_table.setItem(i, 1, QTableWidgetItem(f"{payment['amount']:.2f}"))
            self.payments_table.setItem(i, 2, QTableWidgetItem(payment['reference']))
            
            remove_btn = QPushButton("Remove")
            remove_btn.clicked.connect(lambda checked, idx=i: self.remove_payment(idx))
            self.payments_table.setCellWidget(i, 3, remove_btn)

    def remove_payment(self, index):
        del self.payments[index]
        self.update_payments_table()
        self.update_totals()

    def update_totals(self):
        paid_amount = sum(p['amount'] for p in self.payments)
        remaining = self.total_amount - paid_amount

        self.paid_label.setText(f"Paid: {paid_amount:.2f}")
        self.remaining_label.setText(f"Remaining: {remaining:.2f}")

        if remaining == 0:
            self.ok_button.setEnabled(True)
            self.amount_input.setEnabled(False)
        else:
            self.ok_button.setEnabled(False)
            self.amount_input.setEnabled(True)
            self.amount_input.setText(str(remaining))
