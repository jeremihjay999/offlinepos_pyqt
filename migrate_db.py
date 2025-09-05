"""
Database migration script to update the products table with category and brand relationships.
"""
import sqlite3
from db import POSDatabase

def migrate_database():
    db = POSDatabase()
    
    with db.get_connection() as conn:
        # Add category_id and brand_id columns if they don't exist
        cursor = conn.cursor()
        
        # Check if category_id column exists
        cursor.execute("PRAGMA table_info(products)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'category_id' not in columns:
            print("Adding category_id column to products table...")
            cursor.execute("ALTER TABLE products ADD COLUMN category_id INTEGER REFERENCES categories(id)")
            
        if 'brand_id' not in columns:
            print("Adding brand_id column to products table...")
            cursor.execute("ALTER TABLE products ADD COLUMN brand_id INTEGER REFERENCES brands(id)")
            
        if 'supplier_id' not in columns:
            print("Adding supplier_id column to products table...")
            cursor.execute("ALTER TABLE products ADD COLUMN supplier_id INTEGER REFERENCES suppliers(id)")
            
        # Add foreign key constraints if they don't exist
        cursor.execute("PRAGMA foreign_key_list(products)")
        fk_columns = [fk[3] for fk in cursor.fetchall()]
        
        if 'category_id' not in fk_columns:
            print("Adding foreign key constraint for category_id...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    barcode TEXT UNIQUE,
                    category_id INTEGER,
                    brand_id INTEGER,
                    supplier_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
                    FOREIGN KEY (brand_id) REFERENCES brands(id) ON DELETE SET NULL,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL
                )
            """)
            
            # Copy data to new table
            cursor.execute("""
                INSERT INTO products_new (id, name, description, barcode, created_at)
                SELECT id, name, description, barcode, created_at FROM products
            """)
            
            # Drop old table and rename new one
            cursor.execute("DROP TABLE products")
            cursor.execute("ALTER TABLE products_new RENAME TO products")
            
        conn.commit()
        print("Database migration completed successfully!")

if __name__ == "__main__":
    migrate_database()
