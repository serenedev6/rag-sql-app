# db_connector.py
# PostgreSQL, SQL Server ya SQLite se connect karne ke liye module

import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# DB_TYPE=sqlite, postgresql, or sqlserver
DB_TYPE = os.getenv("DB_TYPE", "postgresql").lower()
SQLITE_PATH = os.getenv("SQLITE_PATH", "sample.db")


def _get_postgresql_connection():
    """PostgreSQL connection using psycopg2"""
    import psycopg2
    
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        port=os.getenv('DB_PORT', '5432')
    )
    print("✅ PostgreSQL se successfully connect ho gaya!")
    return conn


def _get_sqlserver_connection():
    """SQL Server connection using pyodbc"""
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
    PostgreSQL ke liye: DB_TYPE=postgresql (default)
    SQL Server ke liye: DB_TYPE=sqlserver
    """
    try:
        if DB_TYPE == "sqlite":
            conn = sqlite3.connect(SQLITE_PATH)
            print(f"✅ SQLite se connect ho gaya: {SQLITE_PATH}")
            return conn
        elif DB_TYPE == "postgresql":
            return _get_postgresql_connection()
        else:  # sqlserver
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
        if DB_TYPE in ["sqlite", "postgresql"]:
            query = f"SELECT {cols} FROM {table_name} LIMIT {limit}"
        else:  # sqlserver
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
    elif DB_TYPE == "postgresql":
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
    else:  # sqlserver
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
    elif DB_TYPE == "postgresql":
        query = f"""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            AND table_schema = 'public'
            ORDER BY ordinal_position
        """
        df = pd.read_sql(query, conn)
    else:  # sqlserver
        query = f"""
            SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = '{table_name}'
            ORDER BY ORDINAL_POSITION
        """
        df = pd.read_sql(query, conn)

    conn.close()
    return df