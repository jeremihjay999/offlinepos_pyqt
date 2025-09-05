"""
Migration script to:
1. Remove contact_person column from suppliers table
2. Add reorder_level column to variants table
"""
import sqlite3
from db import POSDatabase

def migrate_database():
    db = POSDatabase()
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Remove contact_person from suppliers if it exists
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
        
        # 2. Add reorder_level to variants if it doesn't exist
        cursor.execute("PRAGMA table_info(variants)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'reorder_level' not in columns:
            print("Adding reorder_level column to variants table...")
            cursor.execute('''
                ALTER TABLE variants 
                ADD COLUMN reorder_level INTEGER DEFAULT 5
            ''')
        
        conn.commit()
        print("Database migration completed successfully!")

if __name__ == "__main__":
    migrate_database()
