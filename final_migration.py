"""
Final migration script to:
1. Remove contact_person from suppliers table if it exists
2. Add reorder_level to variants table if it doesn't exist
3. Remove SKU column from variants table
"""
import sqlite3
import os
from datetime import datetime
from db import POSDatabase

def backup_database(db_path):
    """Create a backup of the database before making changes"""
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"Database backed up to: {backup_path}")
        return True
    except Exception as e:
        print(f"Failed to create backup: {e}")
        return False

def migrate_database():
    db_path = "pos_system.db"  # Default path, update if different
    
    # Create backup before making changes
    if not backup_database(db_path):
        print("Warning: Could not create backup. Proceeding anyway...")
    
    db = POSDatabase()
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Enable foreign key support
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        try:
            # 1. Check and remove contact_person from suppliers if it exists
            cursor.execute("PRAGMA table_info(suppliers)")
            columns = [col[1].lower() for col in cursor.fetchall()]
            
            if 'contact_person' in columns:
                print("Removing contact_person column from suppliers table...")
                # Create a new table without the contact_person column
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS suppliers_new (
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
                cursor.execute("DROP TABLE IF EXISTS suppliers_old")
                cursor.execute("ALTER TABLE suppliers RENAME TO suppliers_old")
                cursor.execute("ALTER TABLE suppliers_new RENAME TO suppliers")
                print("Successfully removed contact_person from suppliers table")
            
            # 2. Check and add reorder_level to variants if it doesn't exist
            cursor.execute("PRAGMA table_info(variants)")
            columns = [col[1].lower() for col in cursor.fetchall()]
            
            if 'reorder_level' not in columns:
                print("Adding reorder_level column to variants table...")
                cursor.execute('''
                    ALTER TABLE variants 
                    ADD COLUMN reorder_level INTEGER DEFAULT 5
                ''')
                print("Successfully added reorder_level to variants table")
            
            # 3. Check and remove sku from variants if it exists
            if 'sku' in columns:
                print("Removing sku column from variants table...")
                cursor.execute('''
                    CREATE TABLE variants_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        price REAL NOT NULL,
                        stock_quantity INTEGER DEFAULT 0,
                        reorder_level INTEGER DEFAULT 5,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
                    )
                ''')
                
                # Copy data to new table
                cursor.execute('''
                    INSERT INTO variants_new 
                    (id, product_id, name, price, stock_quantity, reorder_level, created_at)
                    SELECT id, product_id, name, price, stock_quantity, 5, created_at 
                    FROM variants
                ''')
                
                # Drop old table and rename new one
                cursor.execute("DROP TABLE IF EXISTS variants_old")
                cursor.execute("ALTER TABLE variants RENAME TO variants_old")
                cursor.execute("ALTER TABLE variants_new RENAME TO variants")
                print("Successfully removed sku from variants table")
            
            # Rebuild indexes and update statistics
            cursor.execute("ANALYZE")
            conn.commit()
            print("Migration completed successfully!")
            
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Error during migration: {e}")
            print("The database has been rolled back to its original state.")
            return False
        finally:
            # Re-enable foreign key support
            cursor.execute("PRAGMA foreign_keys = ON")
            return True

if __name__ == "__main__":
    migrate_database()
