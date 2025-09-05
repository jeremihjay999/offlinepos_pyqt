from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from db import POSDatabase

class AddSupplierDialog(QDialog):
    def __init__(self, db: POSDatabase, parent=None):
        super().__init__(parent)
        self.db = db
        self.supplier_id = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Add Supplier")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        # Form
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter supplier name")
        form_layout.addRow("Name *:", self.name_input)
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Enter phone number")
        form_layout.addRow("Phone:", self.phone_input)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email address")
        form_layout.addRow("Email:", self.email_input)
        
        self.address_input = QTextEdit()
        self.address_input.setPlaceholderText("Enter supplier address")
        self.address_input.setMaximumHeight(80)
        form_layout.addRow("Address:", self.address_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_supplier)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def save_supplier(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Supplier name is required!")
            return
            
        try:
            self.supplier_id = self.db.create_supplier(
                name=name,
                phone=self.phone_input.text().strip(),
                email=self.email_input.text().strip(),
                address=self.address_input.toPlainText().strip()
            )
            QMessageBox.information(self, "Success", "Supplier added successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add supplier: {str(e)}")

class AddProductDialog(QDialog):
    def __init__(self, db: POSDatabase, parent=None):
        super().__init__(parent)
        self.db = db
        self.product_id = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Add Product")
        self.setFixedSize(500, 600)
        
        layout = QVBoxLayout()
        
        # Product Information
        product_group = QGroupBox("Product Information")
        product_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter product name")
        product_layout.addRow("Name *:", self.name_input)
        
        self.brand_input = QLineEdit()
        self.brand_input.setPlaceholderText("Enter brand name")
        product_layout.addRow("Brand:", self.brand_input)
        
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Enter category")
        product_layout.addRow("Category:", self.category_input)
        
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Enter product barcode (optional)")
        product_layout.addRow("Barcode:", self.barcode_input)
        
        # Supplier selection
        self.supplier_combo = QComboBox()
        self.load_suppliers()
        product_layout.addRow("Supplier:", self.supplier_combo)
        
        product_group.setLayout(product_layout)
        layout.addWidget(product_group)
        
        # Variants Section
        variants_group = QGroupBox("Product Variants")
        variants_layout = QVBoxLayout()
        
        # Variants table
        self.variants_table = QTableWidget()
        self.variants_table.setColumnCount(5)
        self.variants_table.setHorizontalHeaderLabels(['Variant Name', 'Price', 'Barcode', 'Stock', 'Reorder Level'])
        self.variants_table.horizontalHeader().setStretchLastSection(True)
        variants_layout.addWidget(self.variants_table)
        
        # Add variant button
        add_variant_btn = QPushButton("Add Variant")
        add_variant_btn.clicked.connect(self.add_variant_row)
        variants_layout.addWidget(add_variant_btn)
        
        variants_group.setLayout(variants_layout)
        layout.addWidget(variants_group)
        
        # Add first variant row by default
        self.add_variant_row()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Product")
        save_btn.clicked.connect(self.save_product)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def load_suppliers(self):
        """Load suppliers into combo box"""
        self.supplier_combo.addItem("-- No Supplier --", None)
        suppliers = self.db.get_all_suppliers()
        for supplier in suppliers:
            self.supplier_combo.addItem(supplier['name'], supplier['id'])
            
    def add_variant_row(self):
        """Add a new variant row to the table"""
        row = self.variants_table.rowCount()
        self.variants_table.insertRow(row)
        
        # Variant name
        name_input = QLineEdit()
        name_input.setPlaceholderText("e.g., 1kg, 500g")
        self.variants_table.setCellWidget(row, 0, name_input)
        
        # Price
        price_input = QDoubleSpinBox()
        price_input.setRange(0.01, 99999.99)
        price_input.setDecimals(2)
        self.variants_table.setCellWidget(row, 1, price_input)
        
        # Barcode
        barcode_input = QLineEdit()
        barcode_input.setPlaceholderText("Optional")
        self.variants_table.setCellWidget(row, 2, barcode_input)
        
        # Stock
        stock_input = QSpinBox()
        stock_input.setRange(0, 99999)
        self.variants_table.setCellWidget(row, 3, stock_input)
        
        # Reorder level
        reorder_input = QSpinBox()
        reorder_input.setRange(0, 999)
        reorder_input.setValue(10)  # Default reorder level
        self.variants_table.setCellWidget(row, 4, reorder_input)
        
    def save_product(self):
        """Save product and variants"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Product name is required!")
            return
            
        # Check if we have at least one variant
        if self.variants_table.rowCount() == 0:
            QMessageBox.warning(self, "Error", "Please add at least one variant!")
            return
            
        # Validate variants
        variants = []
        for row in range(self.variants_table.rowCount()):
            variant_name_widget = self.variants_table.cellWidget(row, 0)
            price_widget = self.variants_table.cellWidget(row, 1)
            barcode_widget = self.variants_table.cellWidget(row, 2)
            stock_widget = self.variants_table.cellWidget(row, 3)
            reorder_widget = self.variants_table.cellWidget(row, 4)
            
            variant_name = variant_name_widget.text().strip()
            if not variant_name:
                QMessageBox.warning(self, "Error", f"Variant name is required for row {row + 1}!")
                return
                
            price = price_widget.value()
            if price <= 0:
                QMessageBox.warning(self, "Error", f"Price must be greater than 0 for row {row + 1}!")
                return
                
            variants.append({
                'name': variant_name,
                'price': price,
                'barcode': barcode_widget.text().strip(),
                'stock': stock_widget.value(),
                'reorder_level': reorder_widget.value()
            })
            
        try:
            # Get supplier ID
            supplier_id = self.supplier_combo.currentData()
            
            # Create product
            self.product_id = self.db.create_product(
                name=name,
                brand=self.brand_input.text().strip(),
                category=self.category_input.text().strip(),
                barcode=self.barcode_input.text().strip(),
                supplier_id=supplier_id
            )
            
            # Create variants
            for variant in variants:
                self.db.create_variant(
                    product_id=self.product_id,
                    name=variant['name'],
                    price=variant['price'],
                    barcode=variant['barcode'] or None,
                    stock_qty=variant['stock'],
                    reorder_level=variant['reorder_level']
                )
                
            QMessageBox.information(self, "Success", f"Product '{name}' with {len(variants)} variant(s) added successfully!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add product: {str(e)}")

class EditProductDialog(QDialog):
    def __init__(self, db: POSDatabase, product_data: dict, parent=None):
        super().__init__(parent)
        self.db = db
        self.product_data = product_data
        self.init_ui()
        self.load_product_data()
        
    def init_ui(self):
        self.setWindowTitle("Edit Product")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        # Form
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        form_layout.addRow("Product Name:", self.name_input)
        
        self.variant_name_input = QLineEdit()
        form_layout.addRow("Variant Name:", self.variant_name_input)
        
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0.01, 99999.99)
        self.price_input.setDecimals(2)
        form_layout.addRow("Price:", self.price_input)
        
        self.stock_input = QSpinBox()
        self.stock_input.setRange(0, 99999)
        form_layout.addRow("Stock Quantity:", self.stock_input)
        
        self.reorder_input = QSpinBox()
        self.reorder_input.setRange(0, 999)
        form_layout.addRow("Reorder Level:", self.reorder_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_changes)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def load_product_data(self):
        """Load current product data into form"""
        self.name_input.setText(self.product_data.get('product_name', ''))
        self.variant_name_input.setText(self.product_data.get('variant_name', ''))
        self.price_input.setValue(float(self.product_data.get('price', 0)))
        self.stock_input.setValue(int(self.product_data.get('stock_qty', 0)))
        self.reorder_input.setValue(int(self.product_data.get('reorder_level', 10)))
        
    def save_changes(self):
        """Save changes to product/variant"""
        try:
            with self.db.get_connection() as conn:
                # Update product name if changed
                if self.name_input.text().strip() != self.product_data.get('product_name', ''):
                    conn.execute(
                        "UPDATE products SET name = ? WHERE id = ?",
                        (self.name_input.text().strip(), self.product_data['product_id'])
                    )
                
                # Update variant
                conn.execute(
                    "UPDATE variants SET name = ?, price = ?, stock_qty = ?, reorder_level = ? WHERE id = ?",
                    (
                        self.variant_name_input.text().strip(),
                        self.price_input.value(),
                        self.stock_input.value(),
                        self.reorder_input.value(),
                        self.product_data['variant_id']
                    )
                )
                
                conn.commit()
                
            QMessageBox.information(self, "Success", "Product updated successfully!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update product: {str(e)}")

class ReceiptPrintDialog(QDialog):
    def __init__(self, db: POSDatabase, sale_data: dict, parent=None):
        super().__init__(parent)
        self.db = db
        self.sale_data = sale_data
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Receipt Preview")
        self.setFixedSize(400, 600)
        
        layout = QVBoxLayout()
        
        # Receipt preview
        self.receipt_preview = QTextEdit()
        self.receipt_preview.setReadOnly(True)
        self.receipt_preview.setFont(QFont("Courier", 10))
        
        self.generate_receipt_preview()
        
        layout.addWidget(self.receipt_preview)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        print_btn = QPushButton("Print Receipt")
        print_btn.clicked.connect(self.print_receipt)
        
        save_btn = QPushButton("Save as PDF")
        save_btn.clicked.connect(self.save_pdf)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(print_btn)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def generate_receipt_preview(self):
        """Generate receipt preview text"""
        settings = self.db.get_all_settings()
        sale = self.sale_data['sale']
        items = self.sale_data['items']
        
        receipt_text = f"""
{settings.get('store_name', 'POS System').center(32)}
{settings.get('store_address', '').center(32)}
{'=' * 32}

Receipt #: {sale['id']}
Date: {sale['created_at'][:19]}
Cashier: [Current User]

{'=' * 32}
{'ITEM':<20} {'QTY':<4} {'TOTAL':<7}
{'=' * 32}
"""

        for item in items:
            item_name = f"{item['product_name']} ({item['variant_name']})"
            if len(item_name) > 20:
                item_name = item_name[:17] + "..."
            
            receipt_text += f"{item_name:<20} {item['qty']:<4} ${item['subtotal']:<6.2f}\n"
            
        receipt_text += f"""
{'=' * 32}
{'Subtotal:':<25} ${sale['total'] - sale['tax_amount']:<6.2f}
{'Tax:':<25} ${sale['tax_amount']:<6.2f}
{'Discount:':<25} ${sale['discount_amount']:<6.2f}
{'TOTAL:':<25} ${sale['total']:<6.2f}
{'=' * 32}

Payment Method: {sale['payment_method'].title()}

{settings.get('receipt_footer', 'Thank you!').center(32)}

{'-' * 32}
"""
        
        self.receipt_preview.setText(receipt_text)
        
    def print_receipt(self):
        """Print receipt to system printer"""
        try:
            # Create a simple text document for printing
            document = QTextDocument()
            document.setPlainText(self.receipt_preview.toPlainText())
            
            printer = QPrinter()
            printer.setPrinterName("Default")  # Use default printer
            printer.setPaperSize(QPrinter.Custom)
            
            # Print dialog
            print_dialog = QPrintDialog(printer, self)
            if print_dialog.exec_() == QPrintDialog.Accepted:
                document.print_(printer)
                QMessageBox.information(self, "Print", "Receipt sent to printer!")
                
        except Exception as e:
            QMessageBox.warning(self, "Print Error", f"Could not print receipt: {str(e)}")
            
    def save_pdf(self):
        """Save receipt as PDF"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter, A4
            from datetime import datetime
            
            filename, _ = QFileDialog.getSaveFileName(
                self, "Save Receipt", 
                f"receipt_{self.sale_data['sale']['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                "PDF Files (*.pdf)"
            )
            
            if filename:
                c = canvas.Canvas(filename, pagesize=letter)
                width, height = letter
                
                # Write receipt content
                lines = self.receipt_preview.toPlainText().split('\n')
                y_position = height - 50
                
                for line in lines:
                    c.drawString(50, y_position, line)
                    y_position -= 20
                    
                c.save()
                QMessageBox.information(self, "PDF Saved", f"Receipt saved as {filename}")
                
        except ImportError:
            QMessageBox.warning(self, "PDF Error", "ReportLab library not installed. Please install with: pip install reportlab")
        except Exception as e:
            QMessageBox.critical(self, "PDF Error", f"Could not save PDF: {str(e)}")

class EndOfDayDialog(QDialog):
    def __init__(self, db: POSDatabase, shift_data: dict, parent=None):
        super().__init__(parent)
        self.db = db
        self.shift_data = shift_data
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("End of Day Report")
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout()
        
        # Report content
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        
        self.generate_eod_report()
        
        layout.addWidget(self.report_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        export_btn = QPushButton("Export PDF")
        export_btn.clicked.connect(self.export_pdf)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(export_btn)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def generate_eod_report(self):
        """Generate end of day report"""
        shift = self.shift_data
        
        # Get sales data for this shift
        with self.db.get_connection() as conn:
            sales_query = """
                SELECT COUNT(*) as total_sales, SUM(total) as total_revenue,
                       SUM(tax_amount) as total_tax, SUM(discount_amount) as total_discount
                FROM sales 
                WHERE shift_id = ?
            """
            sales_summary = conn.execute(sales_query, (shift['id'],)).fetchone()
            
        start_time = shift['start_time'][:19].replace('T', ' ')
        end_time = shift.get('end_time', 'Current')[:19].replace('T', ' ') if shift.get('end_time') else 'Current'
        
        report_text = f"""
END OF DAY REPORT
=================

Shift Information:
Shift ID: {shift['id']}
Start Time: {start_time}
End Time: {end_time}
Duration: [Calculate based on times]

Cash Summary:
Opening Cash: ${shift['opening_cash']:.2f}
Closing Cash: ${shift.get('closing_cash', 0):.2f}
Difference: ${(shift.get('closing_cash', 0) - shift['opening_cash']):.2f}

Sales Summary:
Total Transactions: {sales_summary['total_sales'] or 0}
Gross Revenue: ${sales_summary['total_revenue'] or 0:.2f}
Tax Collected: ${sales_summary['total_tax'] or 0:.2f}
Discounts Given: ${sales_summary['total_discount'] or 0:.2f}
Net Revenue: ${(sales_summary['total_revenue'] or 0) - (sales_summary['total_discount'] or 0):.2f}

Generated: {QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss')}
"""
        
        self.report_text.setText(report_text)
        
    def export_pdf(self):
        """Export EOD report as PDF"""
        QMessageBox.information(self, "Export", "PDF export functionality will be implemented with ReportLab.")