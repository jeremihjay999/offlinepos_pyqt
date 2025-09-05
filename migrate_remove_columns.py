"""
Migration script to remove:
1. description column from products table
2. contact_person column from suppliers table
"""
import sqlite3
from db import POSDatabase

def migrate_database():
    db = POSDatabase()
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Check if description column exists in products table
        cursor.execute("PRAGMA table_info(products)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'description' in columns:
            print("Removing description column from products table...")
            # Create a new table without the description column
            cursor.execute('''
                CREATE TABLE products_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    barcode TEXT UNIQUE,
                    category_id INTEGER,
                    brand_id INTEGER,
                    supplier_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
                    FOREIGN KEY (brand_id) REFERENCES brands(id) ON DELETE SET NULL,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL
                )
            ''')
            
            # Copy data to new table
            cursor.execute('''
                INSERT INTO products_new 
                (id, name, barcode, category_id, brand_id, supplier_id, created_at)
                SELECT id, name, barcode, category_id, brand_id, supplier_id, created_at 
                FROM products
            ''')
            
            # Drop old table and rename new one
            cursor.execute("DROP TABLE products")
            cursor.execute("ALTER TABLE products_new RENAME TO products")
        
        # Check if contact_person column exists in suppliers table
        cursor.execute("PRAGMA table_info(suppliers)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'contact_person' in columns:
            print("Removing contact_person column from suppliers table...")
            # Create a new table without the contact_person column
            cursor.execute('''
                CREATE TABLE suppliers_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT,
                    email TEXT,
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Copy data to new table
            cursor.execute('''
                INSERT INTO suppliers_new 
                (id, name, phone, email, address, created_at)
                SELECT id, name, phone, email, address, created_at 
                FROM suppliers
            ''')
            
            # Drop old table and rename new one
            cursor.execute("DROP TABLE suppliers")
            cursor.execute("ALTER TABLE suppliers_new RENAME TO suppliers")
        
        conn.commit()
        print("Database migration completed successfully!")

if __name__ == "__main__":
    migrate_database()
