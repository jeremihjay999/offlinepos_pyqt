import sqlite3

def migrate_database():
    conn = sqlite3.connect('pos_system.db')
    cursor = conn.cursor()

    # Create a new variants table without the UNIQUE constraint on barcode
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS variants_new (
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

    # Copy data from the old variants table to the new one
    cursor.execute('INSERT INTO variants_new (id, product_id, name, price, purchase_price, barcode, stock_quantity, reorder_level, created_at) SELECT id, product_id, name, price, purchase_price, barcode, stock_quantity, reorder_level, created_at FROM variants')

    # Drop the old variants table
    cursor.execute('DROP TABLE variants')

    # Rename the new table to variants
    cursor.execute('ALTER TABLE variants_new RENAME TO variants')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    migrate_database()
    print('Database migration for optional barcode completed successfully!')
