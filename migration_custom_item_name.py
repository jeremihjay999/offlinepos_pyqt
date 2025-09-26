import sqlite3

def migrate():
    conn = sqlite3.connect('pos_system.db')
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE sale_items ADD COLUMN name TEXT")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column 'name' already exists in 'sale_items' table.")
        else:
            raise
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
