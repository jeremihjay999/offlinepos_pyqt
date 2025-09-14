import sqlite3

def inspect_db():
    conn = sqlite3.connect('pos_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in the database:")
    for table in tables:
        print(table[0])
    conn.close()

if __name__ == "__main__":
    inspect_db()
