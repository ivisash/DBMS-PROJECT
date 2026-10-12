"""
Pharmacy Prescription and Medicine Stock Management System
Configuration File
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database Backend Selection: 'sqlite' or 'mysql'
# Defaults to 'sqlite' for zero-friction out-of-the-box execution.
# To connect to your local MySQL 8.0 server, set DB_ENGINE = 'mysql'
DB_ENGINE = os.getenv("PHARMACY_DB_ENGINE", "sqlite")

# SQLite Configuration
SQLITE_DB_PATH = os.path.join(BASE_DIR, "pharmacy.db")
SQLITE_SCHEMA_PATH = os.path.join(BASE_DIR, "database", "04_schema_sqlite.sql")

# MySQL Configuration
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "root"),
    "database": os.getenv("MYSQL_DATABASE", "pharmacy_db"),
}
