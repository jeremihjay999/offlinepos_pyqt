import sqlite3

def inspect_db():
    conn = sqlite3.connect('pos_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in the database:")
    for table in tables:
        print(table[0])

    print("\nSchema for sale_items table:")
    cursor.execute("PRAGMA table_info(sale_items)")
    columns = cursor.fetchall()
    for column in columns:
        print(column)

    conn.close()

if __name__ == "__main__":
    inspect_db()
