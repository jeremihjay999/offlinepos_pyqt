"""
Configuration settings for POS System
Modify these settings to customize the application behavior
"""

import os
from pathlib import Path

# Application Settings
APP_NAME = "POS System"
APP_VERSION = "1.0.0"
ORGANIZATION_NAME = "Your Store"

# Database Configuration
DATABASE_PATH = "pos_system.db"  # Path to SQLite database file
DATABASE_BACKUP_DIR = "backups"  # Directory for database backups

# UI Configuration
WINDOW_TITLE = f"{APP_NAME} v{APP_VERSION}"
DEFAULT_WINDOW_SIZE = (1400, 800)
MIN_WINDOW_SIZE = (1200, 700)

# Grid View Settings
PRODUCTS_GRID_COLUMNS = 4  # Number of columns in grid view
PRODUCT_CARD_SIZE = (180, 120)  # Width, Height of product cards

# Colors (can be used in stylesheets)
COLORS = {
    'primary': '#007bff',
    'secondary': '#6c757d',
    'success': '#28a745',
    'warning': '#ffc107',
    'danger': '#dc3545',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40'
}

# Receipt Configuration
RECEIPT_WIDTH_CHARS = 32  # Characters per line on receipt
RECEIPT_LOGO_PATH = "assets/logo.png"  # Path to store logo (optional)

# Barcode Detection Settings
BARCODE_MIN_LENGTH = 8  # Minimum length to consider as barcode
BARCODE_TIMEOUT_MS = 1000  # Milliseconds to wait for complete barcode input

# Stock Management
DEFAULT_REORDER_LEVEL = 10  # Default reorder level for new products
LOW_STOCK_THRESHOLD_RATIO = 1.0  # Show as low stock when qty <= reorder_level * ratio
CRITICAL_STOCK_THRESHOLD_RATIO = 0.5  # Show as critical when qty <= reorder_level * ratio

# Currency and Formatting
DEFAULT_CURRENCY_SYMBOL = "$"
CURRENCY_DECIMAL_PLACES = 2
PRICE_FORMAT = "%.2f"  # Format for displaying prices

# Tax Configuration
DEFAULT_TAX_RATE = 16.0  # Default tax rate percentage
TAX_INCLUSIVE = False  # Whether displayed prices include tax

# Report Configuration
REPORTS_EXPORT_DIR = "reports"  # Directory for exported reports
DEFAULT_REPORT_PERIOD_DAYS = 30  # Default period for reports

# Printer Configuration
RECEIPT_PRINTER_NAME = "Default"  # Default printer name
RECEIPT_PAPER_WIDTH_MM = 80  # Paper width in millimeters (58 or 80 common)

# Security Configuration
PASSWORD_MIN_LENGTH = 6
SESSION_TIMEOUT_MINUTES = 60  # Auto-logout after inactivity (0 = disabled)
BACKUP_RETENTION_DAYS = 30  # Keep backups for this many days

# File Paths
ASSETS_DIR = "assets"
LOGS_DIR = "logs"
TEMP_DIR = "temp"

# Ensure directories exist
def ensure_directories():
    """Create necessary directories if they don't exist"""
    dirs = [
        DATABASE_BACKUP_DIR,
        REPORTS_EXPORT_DIR,
        ASSETS_DIR,
        LOGS_DIR,
        TEMP_DIR
    ]
    
    for directory in dirs:
        Path(directory).mkdir(exist_ok=True)

# Logging Configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'pos_system.log'),
            'mode': 'a',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

# UI Themes
THEMES = {
    'default': {
        'background': '#f8f9fa',
        'surface': '#ffffff',
        'primary': '#007bff',
        'secondary': '#6c757d',
        'accent': '#17a2b8',
        'text': '#212529',
        'text_secondary': '#6c757d'
    },
    'dark': {
        'background': '#343a40',
        'surface': '#495057',
        'primary': '#0d6efd',
        'secondary': '#6c757d',
        'accent': '#20c997',
        'text': '#f8f9fa',
        'text_secondary': '#adb5bd'
    }
}

# Feature Flags
FEATURES = {
    'barcode_scanning': True,
    'receipt_printing': True,
    'multi_currency': False,
    'customer_management': False,  # Future feature
    'loyalty_program': False,      # Future feature
    'promotions': False,           # Future feature
    'online_sync': False,          # Future feature
    'mobile_payments': False,      # Future feature
}

# Default Settings for New Installations
DEFAULT_SETTINGS = {
    'store_name': 'My Store',
    'store_address': '123 Main Street\nCity, State 12345',
    'store_phone': '',
    'store_email': '',
    'currency_symbol': DEFAULT_CURRENCY_SYMBOL,
    'tax_rate': str(DEFAULT_TAX_RATE),
    'receipt_footer': 'Thank you for your business!',
    'receipt_header': '',
    'printer_name': RECEIPT_PRINTER_NAME,
    'receipt_width': str(RECEIPT_PAPER_WIDTH_MM),
    'theme': 'default',
    'auto_backup': 'true',
    'backup_interval_days': '7',
    'session_timeout': str(SESSION_TIMEOUT_MINUTES),
}

# Validation Rules
VALIDATION = {
    'product_name': {
        'required': True,
        'min_length': 2,
        'max_length': 100
    },
    'variant_name': {
        'required': True,
        'min_length': 1,
        'max_length': 50
    },
    'price': {
        'required': True,
        'min_value': 0.01,
        'max_value': 999999.99
    },
    'stock_qty': {
        'required': True,
        'min_value': 0,
        'max_value': 999999
    },
    'supplier_name': {
        'required': True,
        'min_length': 2,
        'max_length': 100
    },
    'username': {
        'required': True,
        'min_length': 3,
        'max_length': 50
    },
    'password': {
        'required': True,
        'min_length': PASSWORD_MIN_LENGTH,
        'max_length': 100
    }
}

# API Configuration (for future online features)
API_CONFIG = {
    'base_url': 'https://api.example.com',
    'timeout_seconds': 30,
    'retry_attempts': 3,
    'api_key': '',  # To be configured by user
}

# Performance Settings
PERFORMANCE = {
    'database_cache_size': 2000,  # SQLite cache size in pages
    'ui_update_interval_ms': 100,  # UI refresh interval
    'search_delay_ms': 300,        # Delay before search execution
    'max_search_results': 100,     # Maximum search results to display
}

# Backup Configuration
BACKUP_CONFIG = {
    'auto_backup_enabled': True,
    'backup_interval_hours': 24,
    'max_backup_files': 10,
    'compress_backups': True,
    'backup_on_close': True
}

# Export Configuration
EXPORT_CONFIG = {
    'csv_delimiter': ',',
    'csv_encoding': 'utf-8',
    'pdf_page_size': 'A4',
    'pdf_font_size': 10,
    'include_headers': True
}

def get_config_value(key, default=None):
    """Get configuration value with fallback to default"""
    return globals().get(key, default)

def update_config_value(key, value):
    """Update configuration value at runtime"""
    globals()[key] = value

def get_theme_colors(theme_name='default'):
    """Get color scheme for specified theme"""
    return THEMES.get(theme_name, THEMES['default'])

def is_feature_enabled(feature_name):
    """Check if a feature is enabled"""
    return FEATURES.get(feature_name, False)

def get_validation_rules(field_name):
    """Get validation rules for a specific field"""
    return VALIDATION.get(field_name, {})

def validate_field(field_name, value):
    """Validate a field value against its rules"""
    rules = get_validation_rules(field_name)
    errors = []
    
    # Required check
    if rules.get('required', False) and not value:
        errors.append(f"{field_name} is required")
        return errors
    
    # Skip other validations if value is empty and not required
    if not value:
        return errors
    
    # String validations
    if isinstance(value, str):
        min_len = rules.get('min_length')
        max_len = rules.get('max_length')
        
        if min_len and len(value) < min_len:
            errors.append(f"{field_name} must be at least {min_len} characters")
        
        if max_len and len(value) > max_len:
            errors.append(f"{field_name} must be no more than {max_len} characters")
    
    # Numeric validations
    if isinstance(value, (int, float)):
        min_val = rules.get('min_value')
        max_val = rules.get('max_value')
        
        if min_val is not None and value < min_val:
            errors.append(f"{field_name} must be at least {min_val}")
        
        if max_val is not None and value > max_val:
            errors.append(f"{field_name} must be no more than {max_val}")
    
    return errors

def load_user_config():
    """Load user-specific configuration from file"""
    config_file = Path("user_config.json")
    if config_file.exists():
        try:
            import json
            with open(config_file, 'r') as f:
                user_config = json.load(f)
            
            # Update global configuration with user settings
            for key, value in user_config.items():
                if key in globals():
                    globals()[key] = value
                    
        except Exception as e:
            print(f"Error loading user config: {e}")

def save_user_config(config_dict):
    """Save user-specific configuration to file"""
    try:
        import json
        with open("user_config.json", 'w') as f:
            json.dump(config_dict, f, indent=2)
    except Exception as e:
        print(f"Error saving user config: {e}")

def get_database_url():
    """Get database connection URL"""
    db_path = Path(DATABASE_PATH)
    if not db_path.is_absolute():
        db_path = Path.cwd() / db_path
    return str(db_path)

def get_stylesheet():
    """Get application stylesheet based on current theme"""
    theme_colors = get_theme_colors()
    
    return f"""
    QMainWindow {{
        background-color: {theme_colors['background']};
        color: {theme_colors['text']};
    }}
    
    QTabWidget::pane {{
        border: 1px solid #dee2e6;
        background-color: {theme_colors['surface']};
    }}
    
    QTabBar::tab {{
        background-color: {theme_colors['secondary']};
        color: {theme_colors['text']};
        padding: 12px 20px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }}
    
    QTabBar::tab:selected {{
        background-color: {theme_colors['surface']};
        border-bottom: 2px solid {theme_colors['primary']};
    }}
    
    QPushButton {{
        background-color: {theme_colors['primary']};
        color: white;
        padding: 8px 16px;
        border: none;
        border-radius: 4px;
        font-weight: bold;
        min-width: 80px;
    }}
    
    QPushButton:hover {{
        background-color: {theme_colors['primary']};
        opacity: 0.9;
    }}
    
    QPushButton:pressed {{
        background-color: {theme_colors['primary']};
        opacity: 0.8;
    }}
    
    QPushButton:disabled {{
        background-color: {theme_colors['secondary']};
        opacity: 0.6;
    }}
    
    QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
        background-color: {theme_colors['surface']};
        border: 2px solid #dee2e6;
        border-radius: 4px;
        padding: 8px;
        color: {theme_colors['text']};
    }}
    
    QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
        border-color: {theme_colors['primary']};
    }}
    
    QTableWidget {{
        background-color: {theme_colors['surface']};
        alternate-background-color: {theme_colors['background']};
        color: {theme_colors['text']};
        gridline-color: #dee2e6;
        selection-background-color: {theme_colors['primary']};
    }}
    
    QHeaderView::section {{
        background-color: {theme_colors['secondary']};
        color: white;
        padding: 8px;
        border: none;
        font-weight: bold;
    }}
    
    QGroupBox {{
        font-weight: bold;
        border: 2px solid #dee2e6;
        border-radius: 4px;
        margin: 10px 0;
        padding-top: 10px;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 10px 0 10px;
    }}
    
    QScrollArea {{
        background-color: {theme_colors['surface']};
        border: 1px solid #dee2e6;
    }}
    
    QFrame {{
        background-color: {theme_colors['surface']};
    }}
    """

# Initialize directories on import
ensure_directories()

# Load user configuration if it exists
load_user_config()

# Version information
VERSION_INFO = {
    'major': 1,
    'minor': 0,
    'patch': 0,
    'build': 1,
    'release_date': '2024-01-01',
    'codename': 'Genesis'
}

def get_version_string():
    """Get formatted version string"""
    v = VERSION_INFO
    return f"{v['major']}.{v['minor']}.{v['patch']}.{v['build']}"

def get_full_version_string():
    """Get full version string with codename"""
    return f"{APP_NAME} v{get_version_string()} '{VERSION_INFO['codename']}'"

# System requirements check
def check_system_requirements():
    """Check if system meets minimum requirements"""
    import sys
    import platform
    
    issues = []
    
    # Python version check
    if sys.version_info < (3, 7):
        issues.append("Python 3.7 or higher is required")
    
    # Platform check
    supported_platforms = ['Windows', 'Linux', 'Darwin']  # Darwin = macOS
    if platform.system() not in supported_platforms:
        issues.append(f"Platform {platform.system()} is not officially supported")
    
    # Memory check (basic)
    try:
        import psutil
        memory_gb = psutil.virtual_memory().total / (1024**3)
        if memory_gb < 2:
            issues.append("At least 2GB RAM recommended")
    except ImportError:
        pass  # psutil not available, skip memory check
    
    return issues

# Development and debugging
DEBUG_MODE = False  # Set to True for development
VERBOSE_LOGGING = False
ENABLE_PROFILING = False

def set_debug_mode(enabled):
    """Enable/disable debug mode"""
    global DEBUG_MODE, VERBOSE_LOGGING
    DEBUG_MODE = enabled
    VERBOSE_LOGGING = enabled
    
    if enabled:
        print(f"Debug mode enabled - {get_full_version_string()}")
        print(f"Database: {get_database_url()}")
        print(f"Python: {sys.version}")

# Configuration summary for troubleshooting
def get_config_summary():
    """Get configuration summary for support/debugging"""
    import platform
    
    return {
        'app_version': get_version_string(),
        'python_version': platform.python_version(),
        'platform': platform.system(),
        'database_path': get_database_url(),
        'features_enabled': [k for k, v in FEATURES.items() if v],
        'theme': 'default',  # Would get from current settings
        'debug_mode': DEBUG_MODE
    }