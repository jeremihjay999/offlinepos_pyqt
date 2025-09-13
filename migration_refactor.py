
import sqlite3

def migrate_database():
    conn = sqlite3.connect('pos_system.db')
    cursor = conn.cursor()

    try:
        # Add purchase_price to variants table
        cursor.execute('ALTER TABLE variants ADD COLUMN purchase_price REAL')
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print('purchase_price column already exists in variants table.')
        else:
            raise

    # Create a new products table without the barcode column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products_new (
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

    # Copy data from the old products table to the new one
    cursor.execute('INSERT INTO products_new (id, name, brand_id, category_id, supplier_id, created_at) SELECT id, name, brand_id, category_id, supplier_id, created_at FROM products')

    # Drop the old products table
    cursor.execute('DROP TABLE products')

    # Rename the new table to products
    cursor.execute('ALTER TABLE products_new RENAME TO products')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    migrate_database()
    print('Database migration completed successfully!')
