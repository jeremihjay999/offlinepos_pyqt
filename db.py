import sqlite3
import hashlib
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class POSDatabase:
    def __init__(self, db_path: str = "pos_system.db"):
        self.db_path = db_path
    
    def get_connection(self):
        """Get database connection with foreign key support"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database with all required tables"""
        with self.get_connection() as conn:
            # Users table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('admin', 'cashier')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Settings table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Categories table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Brands table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS brands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Suppliers table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS suppliers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT,
                    email TEXT,
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Products table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    brand_id INTEGER,
                    category_id INTEGER,
                    supplier_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (brand_id) REFERENCES brands (id),
                    FOREIGN KEY (category_id) REFERENCES categories (id),
                    FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
                )
            ''')
            
            # Variants table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS variants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    name TEXT NOT NULL,  -- e.g., "1kg", "500g"
                    price DECIMAL(10,2) NOT NULL,
                    purchase_price DECIMAL(10,2),
                    barcode TEXT,
                    stock_quantity INTEGER DEFAULT 0,
                    reorder_level INTEGER DEFAULT 10,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')
            
            # Shifts table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS shifts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    opening_cash DECIMAL(10,2) NOT NULL,
                    closing_cash DECIMAL(10,2),
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Sales table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    shift_id INTEGER NOT NULL,
                    total DECIMAL(10,2) NOT NULL,
                    tax_amount DECIMAL(10,2) DEFAULT 0,
                    discount_amount DECIMAL(10,2) DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (shift_id) REFERENCES shifts (id)
                )
            ''')

            # Sale Payments table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sale_payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_id INTEGER NOT NULL,
                    method TEXT NOT NULL,
                    amount REAL NOT NULL,
                    transaction_reference TEXT,
                    FOREIGN KEY (sale_id) REFERENCES sales (id)
                )
            ''')
            
            # Sale Items table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sale_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_id INTEGER NOT NULL,
                    product_id INTEGER,
                    variant_id INTEGER,
                    qty INTEGER NOT NULL,
                    price DECIMAL(10,2) NOT NULL,
                    subtotal DECIMAL(10,2) NOT NULL,
                    FOREIGN KEY (sale_id) REFERENCES sales (id),
                    FOREIGN KEY (product_id) REFERENCES products (id),
                    FOREIGN KEY (variant_id) REFERENCES variants (id)
                )
            ''')
            
            conn.commit()
            self.init_default_data()
    
    def init_default_data(self):
        """Initialize default admin user and settings"""
        with self.get_connection() as conn:
            # Check if admin exists
            admin = conn.execute("SELECT * FROM users WHERE username = 'admin'").fetchone()
            if not admin:
                # Create default admin
                password_hash = hashlib.sha256("admin123".encode()).hexdigest()
                conn.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    ("admin", password_hash, "admin")
                )
            
            # Default settings
            default_settings = [
                ("store_name", "My Store"),
                ("store_address", "123 Main St, City"),
                ("currency_symbol", "$"),
                ("tax_rate", "16.0"),
                ("receipt_footer", "Thank you for shopping with us!"),
                ("printer_name", ""),
                ("receipt_width", "80")
            ]
            
            for key, value in default_settings:
                existing = conn.execute("SELECT * FROM settings WHERE key = ?", (key,)).fetchone()
                if not existing:
                    conn.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (key, value))
            
            conn.commit()
    
    # User Management
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user info"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        with self.get_connection() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE username = ? AND password_hash = ?",
                (username, password_hash)
            ).fetchone()
            return dict(user) if user else None
    
    def create_user(self, username: str, password: str, role: str) -> bool:
        """Create new user"""
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            with self.get_connection() as conn:
                conn.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    (username, password_hash, role)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
    
    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        with self.get_connection() as conn:
            users = conn.execute("SELECT id, username, role, created_at FROM users").fetchall()
            return [dict(user) for user in users]
    
    # Settings Management
    def get_setting(self, key: str) -> str:
        """Get setting value"""
        with self.get_connection() as conn:
            setting = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
            return setting['value'] if setting else ""
    
    def set_setting(self, key: str, value: str):
        """Set setting value"""
        with self.get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, ?)",
                (key, value, datetime.now())
            )
            conn.commit()
    
    def get_all_settings(self) -> Dict[str, str]:
        """Get all settings as dictionary"""
        with self.get_connection() as conn:
            settings = conn.execute("SELECT key, value FROM settings").fetchall()
            return {s['key']: s['value'] for s in settings}
    
    # Category Management
    def add_category(self, name: str, description: str = None) -> int:
        """Add a new category"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)",
                (name, description)
            )
            if cursor.rowcount == 0:
                # Category already exists, get its ID
                cursor.execute("SELECT id FROM categories WHERE name = ?", (name,))
                return cursor.fetchone()['id']
            conn.commit()
            return cursor.lastrowid
    
    def get_all_categories(self) -> List[Dict]:
        """Get all categories"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
    
    # Brand Management
    def add_brand(self, name: str, description: str = None) -> int:
        """Add a new brand"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO brands (name, description) VALUES (?, ?)",
                (name, description)
            )
            if cursor.rowcount == 0:
                # Brand already exists, get its ID
                cursor.execute("SELECT id FROM brands WHERE name = ?", (name,))
                return cursor.fetchone()['id']
            conn.commit()
            return cursor.lastrowid
    
    def get_all_brands(self) -> List[Dict]:
        """Get all brands"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM brands ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
    
    # Supplier Management
    def add_supplier(self, name: str, phone: str = None, 
                    email: str = None, address: str = None) -> int:
        """Add a new supplier"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO suppliers 
                   (name, phone, email, address) 
                   VALUES (?, ?, ?, ?)""",
                (name, phone, email, address)
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_all_suppliers(self) -> List[Dict]:
        """Get all suppliers"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM suppliers ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_supplier(self, supplier_id: int) -> Optional[Dict]:
        """Get supplier by ID"""
        with self.get_connection() as conn:
            supplier = conn.execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,)).fetchone()
            return dict(supplier) if supplier else None
    
    def get_product_by_barcode(self, barcode: str) -> Optional[Dict]:
        """Get product by barcode"""
        with self.get_connection() as conn:
            product = conn.execute("SELECT * FROM products WHERE barcode = ?", (barcode,)).fetchone()
            return dict(product) if product else None
    
    # Product Management
    def add_product(self, name: str, category_id: int = None, 
                   brand_id: int = None, supplier_id: int = None) -> int:
        """
        Add a new product to the database
        
        Args:
            name: Product name
            category_id: ID of the category
            brand_id: ID of the brand
            supplier_id: ID of the supplier
            
        Returns:
            int: The ID of the newly created product
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO products (name, category_id, brand_id, supplier_id)
                VALUES (?, ?, ?, ?)
                """,
                (name, category_id, brand_id, supplier_id)
            )
            product_id = cursor.lastrowid
            conn.commit()
            return product_id
            
    def add_product_variant(self, product_id: int, name: str, price: float, purchase_price: float, barcode: str,
                          stock_quantity: int = 0, reorder_level: int = 5, conn: sqlite3.Connection = None) -> int:
        """
        Add a variant to a product
        
        Args:
            product_id: ID of the product
            name: Variant name (e.g., "500g", "Red")
            price: Price of the variant (as a string to preserve precision)
            purchase_price: Purchase price of the variant
            barcode: Barcode of the variant
            stock_quantity: Initial stock quantity
            reorder_level: Reorder level for this variant (default: 5)
            conn: Optional database connection to use
            
        Returns:
            int: The ID of the newly created variant
        """
        if conn is None:
            conn = self.get_connection()
            close_conn = True
        else:
            close_conn = False

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO variants (product_id, name, price, purchase_price, barcode, stock_quantity, reorder_level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (product_id, name, price, purchase_price, barcode, stock_quantity, reorder_level)
            )
            variant_id = cursor.lastrowid
            if close_conn:
                conn.commit()
            return variant_id
        finally:
            if close_conn:
                conn.close()
    
    
    
    def get_products_with_variants(self) -> List[Dict]:
        """Get all products with their variants and supplier info"""
        with self.get_connection() as conn:
            query = '''
                SELECT 
                    p.id as product_id, p.name as product_name,
                    v.id as variant_id, v.name as variant_name, v.price as price, v.purchase_price, v.barcode as variant_barcode, 
                    v.stock_quantity, v.reorder_level,
                    s.name as supplier_name, s.phone as supplier_phone, s.email as supplier_email,
                    b.name as brand_name,
                    c.name as category_name
                FROM products p
                LEFT JOIN variants v ON p.id = v.product_id
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                LEFT JOIN brands b ON p.brand_id = b.id
                LEFT JOIN categories c ON p.category_id = c.id
                ORDER BY p.name, v.name
            '''
            results = conn.execute(query).fetchall()
            return [dict(row) for row in results]

    def get_product_with_variants_by_id(self, product_id: int) -> Optional[Dict]:
        """Get a single product with its variants and supplier info by product ID"""
        with self.get_connection() as conn:
            query = '''
                SELECT 
                    p.id as product_id, p.name as product_name,
                    v.id as variant_id, v.name as variant_name, v.price as price, v.purchase_price, v.barcode as variant_barcode, 
                    v.stock_quantity, v.reorder_level,
                    s.id as supplier_id, s.name as supplier_name, s.phone as supplier_phone, s.email as supplier_email,
                    b.id as brand_id, b.name as brand_name,
                    c.id as category_id, c.name as category_name
                FROM products p
                LEFT JOIN variants v ON p.id = v.product_id
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                LEFT JOIN brands b ON p.brand_id = b.id
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.id = ?
                ORDER BY p.name, v.name
            '''
            results = conn.execute(query, (product_id,)).fetchall()
            return [dict(row) for row in results][0] if results else None
    
    def search_products(self, search_term: str) -> List[Dict]:
        """Search products by name, brand, or barcode"""
        search_term = f"%{search_term}%"
        with self.get_connection() as conn:
            query = '''
                SELECT 
                    p.id as product_id, p.name as product_name, 
                    v.id as variant_id, v.name as variant_name, v.price, v.purchase_price, v.barcode, 
                    v.stock_quantity, v.reorder_level,
                    b.name as brand_name,
                    c.name as category_name
                FROM products p
                LEFT JOIN variants v ON p.id = v.product_id
                LEFT JOIN brands b ON p.brand_id = b.id
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.name LIKE ? OR b.name LIKE ? OR v.barcode LIKE ?
                ORDER BY p.name, v.name
            '''
            results = conn.execute(query, (search_term, search_term, search_term)).fetchall()
            return [dict(row) for row in results]
    
    def find_by_barcode(self, barcode: str) -> Optional[Dict]:
        """Find product variant by barcode"""
        with self.get_connection() as conn:
            # Check variant barcode first
            query = '''
                SELECT 
                    p.id as product_id, p.name as product_name, 
                    v.id as variant_id, v.name as variant_name, v.price, v.purchase_price, v.stock_quantity,
                    v.id as id,
                    b.name as brand_name,
                    c.name as category_name
                FROM products p
                JOIN variants v ON p.id = v.product_id
                LEFT JOIN brands b ON p.brand_id = b.id
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE v.barcode = ?
            '''
            result = conn.execute(query, (barcode,)).fetchone()
            if result:
                return dict(result)
            return None
    
    def update_stock(self, variant_id: int, quantity_change: int):
        """Update stock quantity for a variant"""
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE variants SET stock_quantity = stock_quantity + ? WHERE id = ?",
                (quantity_change, variant_id)
            )
            conn.commit()
    
    def get_low_stock_items(self) -> List[Dict]:
        """Get items with stock below reorder level"""
        with self.get_connection() as conn:
            query = '''
                SELECT 
                    p.id as product_id, p.name as product_name, 
                    v.id as variant_id, v.name as variant_name, v.price as price, 
                    v.stock_quantity, v.reorder_level,
                    s.name as supplier_name, s.phone as supplier_phone, s.email as supplier_email,
                    b.name as brand_name,
                    c.name as category_name
                FROM products p
                JOIN variants v ON p.id = v.product_id
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                LEFT JOIN brands b ON p.brand_id = b.id
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE v.stock_quantity <= v.reorder_level
                ORDER BY v.stock_quantity ASC
            '''
            results = conn.execute(query).fetchall()
            return [dict(row) for row in results]

    def get_variants_for_product(self, product_id: int, conn: sqlite3.Connection = None) -> List[Dict]:
        """Get all variants for a product"""
        if conn is None:
            conn = self.get_connection()
            close_conn = True
        else:
            close_conn = False
        
        try:
            query = "SELECT * FROM variants WHERE product_id = ? ORDER BY name"
            results = conn.execute(query, (product_id,)).fetchall()
            return [dict(row) for row in results]
        finally:
            if close_conn:
                conn.close()

    def update_product(self, product_id: int, name: str, category_id: int = None,
                     brand_id: int = None, supplier_id: int = None,
                     variants: List[Dict] = []):
        """
        Update a product and its variants.
        """
        with self.get_connection() as conn:
            # Update product details
            conn.execute(
                """
                UPDATE products
                SET name = ?, category_id = ?, brand_id = ?, supplier_id = ?
                WHERE id = ?
                """,
                (name, category_id, brand_id, supplier_id, product_id)
            )

            # Get existing variants
            existing_variants = self.get_variants_for_product(product_id, conn=conn)
            existing_variant_ids = {v['id'] for v in existing_variants}

            # Update or add variants
            for variant in variants:
                variant_id = variant.get('id')
                if variant_id in existing_variant_ids:
                    # Update existing variant
                    conn.execute(
                        """
                        UPDATE variants
                        SET name = ?, price = ?, purchase_price = ?, barcode = ?, stock_quantity = ?, reorder_level = ?
                        WHERE id = ?
                        """,
                        (variant['name'], variant['price'], variant['purchase_price'], variant['barcode'], variant['stock'], variant['reorder_level'], variant_id)
                    )
                    existing_variant_ids.remove(variant_id)
                else:
                    # Add new variant
                    self.add_product_variant(
                        product_id=product_id,
                        name=variant['name'],
                        price=variant['price'],
                        purchase_price=variant['purchase_price'],
                        barcode=variant['barcode'],
                        stock_quantity=variant['stock'],
                        reorder_level=variant['reorder_level'],
                        conn=conn
                    )

            # Remove old variants
            for variant_id in existing_variant_ids:
                conn.execute("DELETE FROM variants WHERE id = ?", (variant_id,))

            conn.commit()
    
    # Shift Management
    def start_shift(self, user_id: int, opening_cash: float) -> int:
        """Start new shift and return shift ID"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO shifts (user_id, opening_cash) VALUES (?, ?)",
                (user_id, opening_cash)
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_active_shift(self, user_id: int) -> Optional[Dict]:
        """Get active shift for user"""
        with self.get_connection() as conn:
            shift = conn.execute(
                "SELECT * FROM shifts WHERE user_id = ? AND end_time IS NULL ORDER BY start_time DESC LIMIT 1",
                (user_id,)
            ).fetchone()
            return dict(shift) if shift else None
    
    def close_shift(self, shift_id: int, closing_cash: float):
        """Close shift"""
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE shifts SET closing_cash = ?, end_time = ? WHERE id = ?",
                (closing_cash, datetime.now(), shift_id)
            )
            conn.commit()
    
    # Sales Management
    def create_sale(self, shift_id: int, total: float, tax_amount: float = 0, 
                   discount_amount: float = 0) -> int:
        """Create sale and return sale ID"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO sales (shift_id, total, tax_amount, discount_amount) VALUES (?, ?, ?, ?)",
                (shift_id, total, tax_amount, discount_amount)
            )
            conn.commit()
            return cursor.lastrowid

    def add_sale_payments(self, sale_id: int, payments: List[Dict]):
        """Add payment records for a sale"""
        with self.get_connection() as conn:
            for payment in payments:
                conn.execute(
                    "INSERT INTO sale_payments (sale_id, method, amount, transaction_reference) VALUES (?, ?, ?, ?)",
                    (sale_id, payment['method'], float(payment['amount']), payment.get('reference'))
                )
            conn.commit()
    
    def add_sale_item(self, sale_id: int, product_id: int, variant_id: int, 
                     qty: int, price: float, subtotal: float):
        """Add item to sale"""
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO sale_items (sale_id, product_id, variant_id, qty, price, subtotal) VALUES (?, ?, ?, ?, ?, ?)",
                (sale_id, product_id, variant_id, qty, price, subtotal)
            )
            # Update stock
            if variant_id:
                conn.execute(
                    "UPDATE variants SET stock_quantity = stock_quantity - ? WHERE id = ?",
                    (qty, variant_id)
                )
            conn.commit()
    
    def get_sale_with_items(self, sale_id: int) -> Dict:
        """Get sale with all items and payments"""
        with self.get_connection() as conn:
            # Get sale info
            sale = conn.execute("SELECT * FROM sales WHERE id = ?", (sale_id,)).fetchone()
            
            # Get sale items
            items_query = '''
                SELECT 
                    si.qty, si.price, si.subtotal,
                    p.name as product_name, 
                    b.name as brand_name,
                    v.name as variant_name
                FROM sale_items si
                JOIN products p ON si.product_id = p.id
                JOIN variants v ON si.variant_id = v.id
                LEFT JOIN brands b ON p.brand_id = b.id
                WHERE si.sale_id = ?
            '''
            items = conn.execute(items_query, (sale_id,)).fetchall()

            # Get sale payments
            payments_query = "SELECT * FROM sale_payments WHERE sale_id = ?"
            payments = conn.execute(payments_query, (sale_id,)).fetchall()
            
            return {
                'sale': dict(sale),
                'items': [dict(item) for item in items],
                'payments': [dict(payment) for payment in payments]
            }
    
    # Reporting
    def get_sales_summary(self, start_date: str = None, end_date: str = None) -> Dict:
        """Get sales summary for date range"""
        with self.get_connection() as conn:
            where_clause = ""
            params = []
            
            if start_date:
                where_clause += " WHERE DATE(s.created_at) >= ?"
                params.append(start_date)
            if end_date:
                where_clause += " AND DATE(s.created_at) <= ?" if where_clause else " WHERE DATE(s.created_at) <= ?"
                params.append(end_date)
            
            # Total sales
            query = f"SELECT COUNT(DISTINCT s.id) as total_sales, SUM(sp.amount) as total_revenue, SUM(s.tax_amount) as total_tax, SUM(s.discount_amount) as total_discounts FROM sales s JOIN sale_payments sp ON s.id = sp.sale_id{where_clause}"
            summary = conn.execute(query, params).fetchone()

            # Revenue by payment method
            payment_method_query = f'''
                SELECT method, SUM(amount) as total
                FROM sale_payments sp
                JOIN sales s ON sp.sale_id = s.id
                {where_clause}
                GROUP BY method
            '''
            payment_methods = conn.execute(payment_method_query, params).fetchall()
            
            # Top products
            top_products_query = f'''
                SELECT 
                    p.name as product_name, v.name as variant_name,
                    SUM(si.qty) as total_qty, SUM(si.subtotal) as total_revenue
                FROM sale_items si
                JOIN products p ON si.product_id = p.id
                JOIN variants v ON si.variant_id = v.id
                JOIN sales s ON si.sale_id = s.id
                {where_clause}
                GROUP BY si.product_id, si.variant_id
                ORDER BY total_qty DESC
                LIMIT 10
            '''
            top_products = conn.execute(top_products_query, params).fetchall()
            
            return {
                'summary': dict(summary),
                'payment_methods': [dict(pm) for pm in payment_methods],
                'top_products': [dict(product) for product in top_products]
            }

    def get_total_sales(self, start_date: str, end_date: str) -> float:
        with self.get_connection() as conn:
            query = "SELECT SUM(amount) FROM sale_payments sp JOIN sales s ON sp.sale_id = s.id WHERE DATE(s.created_at) BETWEEN ? AND ?"
            result = conn.execute(query, (start_date, end_date)).fetchone()
            return result[0] or 0

    def get_number_of_sales(self, start_date: str, end_date: str) -> int:
        with self.get_connection() as conn:
            query = "SELECT COUNT(DISTINCT sale_id) FROM sale_payments sp JOIN sales s ON sp.sale_id = s.id WHERE DATE(s.created_at) BETWEEN ? AND ?"
            result = conn.execute(query, (start_date, end_date)).fetchone()
            return result[0] or 0

    def get_items_sold(self, start_date: str, end_date: str) -> int:
        with self.get_connection() as conn:
            query = "SELECT SUM(qty) FROM sale_items si JOIN sales s ON si.sale_id = s.id WHERE DATE(s.created_at) BETWEEN ? AND ?"
            result = conn.execute(query, (start_date, end_date)).fetchone()
            return result[0] or 0

    def get_profit(self, start_date: str, end_date: str) -> float:
        with self.get_connection() as conn:
            query = """
                SELECT SUM(si.subtotal - (v.purchase_price * si.qty))
                FROM sale_items si
                JOIN variants v ON si.variant_id = v.id
                JOIN sales s ON si.sale_id = s.id
                WHERE v.purchase_price IS NOT NULL AND DATE(s.created_at) BETWEEN ? AND ?
            """
            result = conn.execute(query, (start_date, end_date)).fetchone()
            return result[0] or 0

    def get_sales_by_payment_method(self, start_date: str, end_date: str) -> List[Dict]:
        with self.get_connection() as conn:
            query = """
                SELECT method, SUM(amount) as total
                FROM sale_payments sp
                JOIN sales s ON sp.sale_id = s.id
                WHERE DATE(s.created_at) BETWEEN ? AND ?
                GROUP BY method
            """
            results = conn.execute(query, (start_date, end_date)).fetchall()
            return [dict(row) for row in results]

    def get_top_products(self, start_date: str, end_date: str) -> List[Dict]:
        with self.get_connection() as conn:
            query = """
                SELECT
                    p.name as product_name,
                    v.name as variant_name,
                    SUM(si.qty) as total_qty,
                    SUM(si.subtotal) as total_revenue,
                    SUM(si.subtotal - (v.purchase_price * si.qty)) as total_profit
                FROM sale_items si
                JOIN products p ON si.product_id = p.id
                JOIN variants v ON si.variant_id = v.id
                JOIN sales s ON si.sale_id = s.id
                WHERE v.purchase_price IS NOT NULL AND DATE(s.created_at) BETWEEN ? AND ?
                GROUP BY si.product_id, si.variant_id
                ORDER BY total_qty DESC
                LIMIT 10
            """
            results = conn.execute(query, (start_date, end_date)).fetchall()
            return [dict(row) for row in results]

    def get_detailed_sales(self, start_date: str, end_date: str) -> List[Dict]:
        with self.get_connection() as conn:
            query = """
                SELECT
                    s.id as sale_id,
                    s.created_at as sale_date,
                    s.total as total_amount,
                    GROUP_CONCAT(sp.method || ': ' || sp.amount) as payments,
                    'Completed' as status
                FROM sales s
                JOIN sale_payments sp ON s.id = sp.sale_id
                WHERE DATE(s.created_at) BETWEEN ? AND ?
                GROUP BY s.id
                ORDER BY s.created_at DESC
            """
            results = conn.execute(query, (start_date, end_date)).fetchall()
            return [dict(row) for row in results]

    def get_items_sold_for_sale(self, sale_id: int) -> int:
        with self.get_connection() as conn:
            query = "SELECT SUM(qty) FROM sale_items WHERE sale_id = ?"
            result = conn.execute(query, (sale_id,)).fetchone()
            return result[0] or 0