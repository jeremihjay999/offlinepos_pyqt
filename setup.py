"""
Setup script for POS System
This script helps with installation and building the executable
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing requirements: {e}")
        return False
    return True

def create_executable():
    """Create standalone executable using PyInstaller"""
    print("Creating executable...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "POS_System",
        "--icon", "icon.ico",  # Add if you have an icon
        "main.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("✓ Executable created successfully!")
        print("Find your executable in the 'dist' folder")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error creating executable: {e}")
        return False
    except FileNotFoundError:
        print("✗ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        try:
            subprocess.check_call(cmd)
            print("✓ Executable created successfully!")
        except subprocess.CalledProcessError as e:
            print(f"✗ Error creating executable: {e}")
            return False
    return True

def create_sample_data():
    """Create sample data for testing"""
    print("Creating sample data...")
    
    from db import POSDatabase
    
    db = POSDatabase("pos_system.db")
    
    # Add sample suppliers
    supplier1_id = db.create_supplier("ABC Wholesale", "+254-700-123456", "abc@wholesale.com", "123 Market Street")
    supplier2_id = db.create_supplier("XYZ Distributors", "+254-700-789012", "info@xyz.com", "456 Industrial Area")
    
    # Add sample products with variants
    # Rice products
    rice_id = db.create_product("Basmati Rice", "Pishori", "Grains", "1234567890123", supplier1_id)
    db.create_variant(rice_id, "1kg", 150.00, "1234567890124", 50, 10)
    db.create_variant(rice_id, "2kg", 280.00, "1234567890125", 30, 5)
    
    # Cooking oil
    oil_id = db.create_product("Cooking Oil", "Fresh Fri", "Oil", "2234567890123", supplier1_id)
    db.create_variant(oil_id, "500ml", 120.00, "2234567890124", 40, 8)
    db.create_variant(oil_id, "1L", 220.00, "2234567890125", 25, 5)
    
    # Bread
    bread_id = db.create_product("Bread", "Festive", "Bakery", "3234567890123", supplier2_id)
    db.create_variant(bread_id, "400g", 50.00, "3234567890124", 20, 15)
    db.create_variant(bread_id, "800g", 85.00, "3234567890125", 15, 10)
    
    # Milk
    milk_id = db.create_product("Fresh Milk", "Brookside", "Dairy", "4234567890123", supplier2_id)
    db.create_variant(milk_id, "500ml", 60.00, "4234567890124", 30, 10)
    db.create_variant(milk_id, "1L", 110.00, "4234567890125", 20, 8)
    
    # Sugar
    sugar_id = db.create_product("White Sugar", "Kabras", "Sweeteners", "5234567890123", supplier1_id)
    db.create_variant(sugar_id, "1kg", 120.00, "5234567890124", 25, 5)
    db.create_variant(sugar_id, "2kg", 230.00, "5234567890125", 15, 3)
    
    # Tea
    tea_id = db.create_product("Black Tea", "Kericho Gold", "Beverages", "6234567890123", supplier2_id)
    db.create_variant(tea_id, "250g", 180.00, "6234567890124", 35, 8)
    db.create_variant(tea_id, "500g", 340.00, "6234567890125", 20, 5)
    
    # Soap
    soap_id = db.create_product("Laundry Soap", "Omo", "Cleaning", "7234567890123", supplier2_id)
    db.create_variant(soap_id, "500g", 85.00, "7234567890124", 40, 10)
    db.create_variant(soap_id, "1kg", 160.00, "7234567890125", 25, 8)
    
    # Set some items to low stock for testing reorder feature
    db.update_stock(1, -45)  # Rice 1kg: 50 - 45 = 5 (below reorder level of 10)
    db.update_stock(7, -12)  # Bread 400g: 20 - 12 = 8 (below reorder level of 15)
    
    print("✓ Sample data created successfully!")
    print("Sample products added with low stock items for testing reorder feature.")

def cleanup_build_files():
    """Clean up build files"""
    print("Cleaning up build files...")
    
    dirs_to_remove = ["build", "__pycache__", "dist"]
    files_to_remove = ["*.spec"]
    
    for directory in dirs_to_remove:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"Removed {directory}")
    
    import glob
    for pattern in files_to_remove:
        for file in glob.glob(pattern):
            os.remove(file)
            print(f"Removed {file}")
    
    print("✓ Cleanup completed!")

def create_project_structure():
    """Create proper project structure"""
    print("Creating project structure...")
    
    # Create directories
    directories = [
        "backups",
        "receipts", 
        "reports",
        "assets",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"Created directory: {directory}")
    
    print("✓ Project structure created!")

def run_tests():
    """Run basic functionality tests"""
    print("Running basic tests...")
    
    try:
        from db import POSDatabase
        
        # Test database initialization
        db = POSDatabase(":memory:")  # Use in-memory database for testing
        
        # Test user creation
        result = db.create_user("testuser", "testpass", "cashier")
        assert result == True, "User creation failed"
        
        # Test authentication
        user = db.authenticate_user("testuser", "testpass")
        assert user is not None, "Authentication failed"
        assert user['username'] == "testuser", "Wrong user returned"
        
        # Test supplier creation
        supplier_id = db.create_supplier("Test Supplier", "123-456-7890", "test@supplier.com", "Test Address")
        assert supplier_id > 0, "Supplier creation failed"
        
        # Test product creation
        product_id = db.create_product("Test Product", "Test Brand", "Test Category", "1111111111111", supplier_id)
        assert product_id > 0, "Product creation failed"
        
        # Test variant creation
        variant_id = db.create_variant(product_id, "Test Variant", 10.99, "2222222222222", 100, 10)
        assert variant_id > 0, "Variant creation failed"
        
        print("✓ All tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("POS System Setup")
    print("================")
    
    if len(sys.argv) < 2:
        print("Usage: python setup.py <command>")
        print("Commands:")
        print("  install     - Install requirements")
        print("  build       - Create executable")
        print("  sample      - Create sample data")
        print("  clean       - Clean build files")
        print("  structure   - Create project structure")
        print("  test        - Run basic tests")
        print("  full        - Run full setup (install + structure + sample)")
        return
    
    command = sys.argv[1].lower()
    
    if command == "install":
        install_requirements()
    elif command == "build":
        if install_requirements():
            create_executable()
    elif command == "sample":
        create_sample_data()
    elif command == "clean":
        cleanup_build_files()
    elif command == "structure":
        create_project_structure()
    elif command == "test":
        run_tests()
    elif command == "full":
        print("Running full setup...")
        if install_requirements():
            create_project_structure()
            create_sample_data()
            print("✓ Full setup completed!")
        else:
            print("✗ Setup failed!")
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()