import sqlite3

def migrate_database():
    conn = sqlite3.connect('pos_system.db')
    cursor = conn.cursor()

    try:
        cursor.execute('ALTER TABLE sales ADD COLUMN payment_method TEXT')
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print('payment_method column already exists in sales table.')
        else:
            raise

    try:
        cursor.execute('ALTER TABLE sales ADD COLUMN transaction_reference TEXT')
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print('transaction_reference column already exists in sales table.')
        else:
            raise

    try:
        cursor.execute('ALTER TABLE sales ADD COLUMN amount_paid REAL')
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print('amount_paid column already exists in sales table.')
        else:
            raise

    conn.commit()
    conn.close()

if __name__ == '__main__':
    migrate_database()
    print('Database migration for sales table completed successfully!')
