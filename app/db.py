"""
Database Access Layer
Supports SQLite and MySQL with unified query execution.
"""
import sqlite3
import os
from app.config import DB_ENGINE, SQLITE_DB_PATH, SQLITE_SCHEMA_PATH, MYSQL_CONFIG

try:
    import mysql.connector
except ImportError:
    mysql = None


def get_connection():
    """Returns an active database connection."""
    if DB_ENGINE == "mysql":
        if mysql is None:
            raise RuntimeError("mysql-connector-python is not installed.")
        return mysql.connector.connect(**MYSQL_CONFIG)
    else:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn


def init_database():
    """Initializes SQLite database with schema and seed data if not already created."""
    if DB_ENGINE == "sqlite":
        if not os.path.exists(SQLITE_DB_PATH):
            print(f"[+] Initializing new SQLite database at {SQLITE_DB_PATH}...")
            conn = sqlite3.connect(SQLITE_DB_PATH)
            with open(SQLITE_SCHEMA_PATH, "r", encoding="utf-8") as f:
                schema_script = f.read()
            conn.executescript(schema_script)
            conn.commit()
            conn.close()
            print("[OK] SQLite database initialized with tables and sample seed records.")


def execute_query(query, params=(), commit=False):
    """
    Executes a SELECT or DML query.
    Returns (rows, lastrowid, cursor.description)
    """
    init_database()
    conn = get_connection()
    try:
        if DB_ENGINE == "sqlite":
            cursor = conn.cursor()
            cursor.execute(query, params)
            if commit:
                conn.commit()
                last_id = cursor.lastrowid
                return [], last_id, cursor.description
            rows = [dict(row) for row in cursor.fetchall()]
            return rows, None, cursor.description
        else:
            cursor = conn.cursor(dictionary=True)
            # Replace ? with %s for MySQL compatibility
            formatted_query = query.replace("?", "%s")
            cursor.execute(formatted_query, params)
            if commit:
                conn.commit()
                last_id = cursor.lastrowid
                return [], last_id, cursor.description
            rows = cursor.fetchall()
            return rows, None, cursor.description
    finally:
        conn.close()
