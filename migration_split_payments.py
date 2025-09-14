import sqlite3

def migrate():
    conn = sqlite3.connect('pos_system.db')
    cursor = conn.cursor()

    # 1. Create the new sale_payments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sale_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            method TEXT NOT NULL,
            amount REAL NOT NULL,
            transaction_reference TEXT,
            FOREIGN KEY (sale_id) REFERENCES sales (id)
        )
    ''')

    # 2. Rename the existing sales table
    cursor.execute('ALTER TABLE sales RENAME TO sales_old')

    # 3. Create the new sales table without the payment columns
    cursor.execute('''
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shift_id INTEGER NOT NULL,
            total DECIMAL(10,2) NOT NULL,
            tax_amount DECIMAL(10,2) DEFAULT 0,
            discount_amount DECIMAL(10,2) DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (shift_id) REFERENCES shifts (id)
        )
    ''')

    # 4. Copy data from sales_old to the new sales table
    cursor.execute('''
        INSERT INTO sales (id, shift_id, total, tax_amount, discount_amount, created_at)
        SELECT id, shift_id, total, tax_amount, discount_amount, created_at FROM sales_old
    ''')

    # 5. Populate the sale_payments table from sales_old
    cursor.execute('''
        INSERT INTO sale_payments (sale_id, method, amount, transaction_reference)
        SELECT id, COALESCE(payment_method, 'Cash'), COALESCE(amount_paid, 0), transaction_reference FROM sales_old
    ''')

    # 6. Drop the old sales table
    cursor.execute('DROP TABLE sales_old')

    conn.commit()
    conn.close()
    print("Migration to split payments completed successfully.")

if __name__ == "__main__":
    migrate()
