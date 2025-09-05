# Offline POS (Point of Sale) System

A complete, modern, fully offline Point of Sale desktop application built with Python and SQLite. Perfect for small to medium businesses that need a reliable cash register system without internet dependency.

![POS System](https://img.shields.io/badge/Python-3.7+-blue.svg)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green.svg)
![SQLite](https://img.shields.io/badge/Database-SQLite-orange.svg)
![License](https://img.shields.io/badge/License-MIT-red.svg)

## 🌟 Features

### Core Functionality
- **Fully Offline Operation** - No internet required
- **Modern GUI** - Clean, intuitive interface with grid and table views
- **Barcode Scanning Support** - Compatible with USB barcode scanners
- **Receipt Printing** - Print receipts to thermal or regular printers
- **Multi-User Support** - Admin and Cashier roles with permissions
- **Shift Management** - Opening/closing cash tracking with EOD reports

### Product Management
- **Product Variants** - Handle different sizes, weights, flavors
- **Stock Tracking** - Real-time inventory management
- **Supplier Integration** - Track suppliers with contact information
- **Reorder Alerts** - Automatic low stock notifications with supplier details
- **Category Management** - Organize products by brand and category

### Sales Features
- **Flexible Cart System** - Add, remove, modify quantities
- **Tax Calculations** - Configurable tax rates
- **Multiple Payment Methods** - Cash (with plans for card/mobile money)
- **Discount Support** - Apply discounts to transactions
- **Receipt Preview** - Preview before printing

### Reporting & Analytics
- **End-of-Day Reports** - Automatic shift closing reports
- **Sales Summaries** - Daily, weekly, monthly, annual views
- **Top Products Analysis** - Best-selling items tracking
- **Cash Reconciliation** - Expected vs actual cash tracking
- **Export Capabilities** - CSV and PDF export options

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- Windows, macOS, or Linux
- USB barcode scanner (optional)
- Thermal or regular printer (optional)

### Installation

1. **Clone or Download**
   ```bash
   git clone <repository-url>
   cd pos-system
   ```

2. **Install Dependencies**
   ```bash
   python setup.py install
   ```
   Or manually:
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize with Sample Data** (Optional)
   ```bash
   python setup.py sample
   ```

4. **Run the Application**
   ```bash
   python main.py
   ```

### Default Login
- **Username**: `admin`
- **Password**: `admin123`

## 📋 Setup Commands

Use the setup script for easy installation and configuration:

```bash
# Full setup (recommended for first time)
python setup.py full

# Individual commands
python setup.py install     # Install requirements
python setup.py structure   # Create project folders
python setup.py sample      # Add sample data
python setup.py test        # Run basic tests
python setup.py build       # Create executable
python setup.py clean       # Clean build files
```

## 🏪 Usage Guide

### For Administrators

1. **Initial Setup**
   - Login with admin credentials
   - Go to Settings tab to configure store information
   - Add suppliers and products
   - Create cashier users

2. **Product Management**
   - Use "Products" tab to manage inventory
   - Add products with variants (sizes, weights, etc.)
   - Set reorder levels for automatic alerts
   - Monitor stock levels and reorder when needed

3. **User Management**
   - Create cashier accounts in Settings
   - Assign appropriate roles and permissions

### For Cashiers

1. **Starting a Shift**
   - Login with cashier credentials
   - Enter opening cash amount
   - Begin processing sales

2. **Processing Sales**
   - Search products or scan barcodes
   - Add items to cart
   - Adjust quantities as needed
   - Process payment and print receipt

3. **Closing Shift**
   - Use Shift → Close Shift menu
   - Enter actual cash amount
   - Review End-of-Day report

### Barcode Scanning

The system supports USB barcode scanners that emulate keyboard input:

1. **Setup**: Connect scanner to USB port (no drivers needed)
2. **Usage**: Scan barcode in search field or anywhere in sales interface
3. **Detection**: System auto-detects barcode format and adds items to cart

### Reorder Management

When stock is low:

1. **Alerts**: Products below reorder level are highlighted in yellow/red
2. **Reorder Button**: Click "Re-order" to see supplier contact information
3. **Contact Supplier**: Use provided phone/email to place orders
4. **Update Stock**: Manually update quantities when items arrive

## 🛠️ Technical Details

### Architecture
- **Database**: SQLite for local data storage
- **GUI Framework**: PyQt5 for cross-platform desktop interface
- **Reports**: ReportLab for PDF generation
- **Packaging**: PyInstaller for standalone executables

### Database Schema
- **Users**: Authentication and role management
- **Products/Variants**: Inventory with multiple variants per product
- **Suppliers**: Contact information and product relationships
- **Sales/Items**: Transaction records with detailed line items
- **Shifts**: Cash drawer management and EOD tracking
- **Settings**: Configurable application parameters

### File Structure
```
pos-system/
├── main.py              # Main application entry point
├── db.py                # Database layer and models
├── dialogs.py           # Dialog windows (add/edit forms)
├── setup.py             # Installation and setup script
├── requirements.txt     # Python dependencies
├── pos_system.db        # SQLite database (created on first run)
├── backups/            # Database backups
├── receipts/           # Receipt templates and output
├── reports/            # Generated reports
└── assets/             # Images, icons, etc.
```

## 📊 Sample Data

The system includes sample data for testing:
- **Suppliers**: ABC Wholesale, XYZ Distributors
- **Products**: Rice, Cooking Oil, Bread, Milk, Sugar, Tea, Soap
- **Variants**: Different sizes and weights per product
- **Stock Levels**: Some items set to low stock for testing reorder feature

## 🔧 Configuration

### Store Settings
Configure in Settings tab (Admin only):
- Store name and address
- Currency symbol and formatting
- Tax rates
- Receipt footer message
- Printer preferences

### Database Location
By default, the database file `pos_system.db` is created in the application directory. You can specify a different location by modifying the database path in `main.py`.

### Backup Strategy
- Use File → Backup Database menu for manual backups
- Database file can be copied directly for backup
- Consider regular automated backups for production use

## 🔒 Security Features

- **Password Hashing**: All passwords are stored as SHA-256 hashes
- **Role-Based Access**: Admin and Cashier roles with different permissions
- **Session Management**: Shift-based access control
- **Data Integrity**: Foreign key constraints and transaction safety

## 📈 Building Executable

Create a standalone executable for distribution:

```bash
python setup.py build
```

This creates:
- **Windows**: `dist/POS_System.exe`
- **macOS**: `dist/POS_System.app`
- **Linux**: `dist/POS_System`

The executable includes all dependencies and can run without Python installation.

## 🚧 Future Enhancements

- **Mobile Payment Integration** (M-Pesa, Card payments)
- **Multi-Store Synchronization**
- **Customer Management & Loyalty Programs**
- **Advanced Reporting Dashboard**
- **Promotion & Discount Management**
- **Multi-Language Support**
- **Cloud Backup Integration**
- **Inventory Purchase Orders (PDF generation)**

## 🐛 Troubleshooting

### Common Issues

1. **Database Permission Errors**
   - Ensure write permissions in application directory
   - Run as administrator if necessary

2. **Printer Not Found**
   - Check printer drivers and connections
   - Verify printer name in Settings

3. **Barcode Scanner Not Working**
   - Ensure scanner is set to keyboard emulation mode
   - Test scanner in text editor first

4. **Import Errors**
   - Reinstall requirements: `python setup.py install`
   - Check Python version compatibility

### Getting Help

1. **Check Logs**: Application logs are stored in `logs/` directory
2. **Test Database**: Run `python setup.py test` to verify functionality
3. **Reset Database**: Delete `pos_system.db` to start fresh
4. **Sample Data**: Use `python setup.py sample` to reload test data

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python setup.py test`
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section above
- Review the sample data and test functionality

---

**Built with ❤️ for small businesses needing reliable offline POS solutions.**