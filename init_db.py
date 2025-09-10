from db import POSDatabase

def initialize_database():
    # Initialize database and create tables
    db = POSDatabase()
    db.init_database()
    
    # Create default admin user if it doesn't exist
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Check if admin user exists
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            # Create default admin user (username: admin, password: admin123)
            password_hash = hashlib.sha256('admin123'.encode('utf-8')).hexdigest()
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                ('admin', password_hash, 'admin')
            )
            print("Default admin user created successfully!")
            print("Username: admin")
            print("Password: admin123")
        else:
            print("Admin user already exists.")
    
    print("Database initialization complete!")

if __name__ == "__main__":
    initialize_database()
