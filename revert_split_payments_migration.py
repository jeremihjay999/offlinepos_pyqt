import sqlite3

def revert():
    conn = sqlite3.connect('pos_system.db')
    cursor = conn.cursor()

    try:
        # Drop the sale_payments table if it exists
        cursor.execute('DROP TABLE IF EXISTS sale_payments')

        # Drop the new sales table if it exists
        cursor.execute('DROP TABLE IF EXISTS sales')

        # Rename sales_old back to sales if it exists
        cursor.execute('ALTER TABLE sales_old RENAME TO sales')

        print("Reverted the partial split payments migration.")
    except sqlite3.OperationalError as e:
        print(f"An error occurred during revert: {e}")
        print("It's possible the database is in the state before the migration was attempted.")


    conn.commit()
    conn.close()

if __name__ == "__main__":
    revert()
