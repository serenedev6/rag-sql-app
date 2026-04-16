# db_connector.py
# SQL Server ya SQLite se connect karne ke liye module

import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# DB_TYPE=sqlite set karo .env mein SQLite use karne ke liye
DB_TYPE = os.getenv("DB_TYPE", "sqlserver").lower()
SQLITE_PATH = os.getenv("SQLITE_PATH", "sample.db")


def _get_sqlserver_connection():
    import pyodbc
    use_windows_auth = os.getenv("USE_WINDOWS_AUTH", "no").lower() == "yes"

    if use_windows_auth:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={os.getenv('SQL_SERVER')};"
            f"DATABASE={os.getenv('SQL_DATABASE')};"
            f"Trusted_Connection=yes;"
        )
    else:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={os.getenv('SQL_SERVER')};"
            f"DATABASE={os.getenv('SQL_DATABASE')};"
            f"UID={os.getenv('SQL_USERNAME')};"
            f"PWD={os.getenv('SQL_PASSWORD')};"
        )

    conn = pyodbc.connect(conn_str)
    print("✅ SQL Server se successfully connect ho gaya!")
    return conn


def get_connection():
    """
    DB_TYPE ke hisaab se connection banata hai.
    SQLite ke liye: DB_TYPE=sqlite in .env
    SQL Server ke liye: DB_TYPE=sqlserver (default)
    """
    try:
        if DB_TYPE == "sqlite":
            conn = sqlite3.connect(SQLITE_PATH)
            print(f"✅ SQLite se connect ho gaya: {SQLITE_PATH}")
            return conn
        else:
            return _get_sqlserver_connection()
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        raise


def fetch_table_data(table_name: str, columns: list = None, limit: int = None) -> pd.DataFrame:
    """
    Table se data fetch karta hai.

    Args:
        table_name: Table ka naam
        columns: Specific columns (None = sab columns)
        limit: Kitne rows chahiye (None = sab)

    Returns:
        DataFrame with fetched data
    """
    conn = get_connection()

    cols = ", ".join(columns) if columns else "*"

    if limit:
        if DB_TYPE == "sqlite":
            query = f"SELECT {cols} FROM {table_name} LIMIT {limit}"
        else:
            query = f"SELECT TOP {limit} {cols} FROM {table_name}"
    else:
        query = f"SELECT {cols} FROM {table_name}"

    df = pd.read_sql(query, conn)
    conn.close()

    print(f"✅ {len(df)} rows fetch kiye '{table_name}' se")
    return df


def fetch_custom_query(query: str) -> pd.DataFrame:
    """
    Custom SQL query run karta hai.
    """
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def get_all_tables() -> list:
    """
    Database mein saari tables ki list deta hai.
    """
    conn = get_connection()
    cursor = conn.cursor()

    if DB_TYPE == "sqlite":
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    else:
        cursor.execute("""
            SELECT TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)

    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables


def get_table_schema(table_name: str) -> pd.DataFrame:
    """
    Table ka schema deta hai.
    """
    conn = get_connection()

    if DB_TYPE == "sqlite":
        df = pd.read_sql(f"PRAGMA table_info({table_name})", conn)
    else:
        query = f"""
            SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = '{table_name}'
            ORDER BY ORDINAL_POSITION
        """
        df = pd.read_sql(query, conn)

    conn.close()
    return df
