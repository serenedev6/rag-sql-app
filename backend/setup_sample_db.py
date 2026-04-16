# setup_sample_db.py
# Creates a sample SQLite database with products, customers, and orders data

import sqlite3
import os

DB_PATH = "sample.db"


def create_sample_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Products table
    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            product_name TEXT,
            category TEXT,
            price REAL,
            stock INTEGER,
            description TEXT
        )
    """)
    cursor.executemany("INSERT INTO products VALUES (?,?,?,?,?,?)", [
        (1,  "Laptop Pro 15",       "Electronics",  75000, 50,  "High performance laptop with 16GB RAM, 512GB SSD, Intel i7 processor. Great for developers and designers."),
        (2,  "Wireless Headphones", "Electronics",  3500,  200, "Noise-cancelling over-ear headphones with 30-hour battery life and Bluetooth 5.0."),
        (3,  "Smartphone X12",      "Electronics",  35000, 120, "Latest flagship smartphone with 5G support, 108MP camera, and 6.7-inch AMOLED display."),
        (4,  "Washing Machine 7kg", "Appliances",   28000, 30,  "Fully automatic front load washing machine with 15 wash programs and energy star rating."),
        (5,  "Refrigerator 350L",   "Appliances",   42000, 25,  "Double door frost-free refrigerator with inverter compressor and vegetable crisper."),
        (6,  "Running Shoes",       "Sports",       4500,  300, "Lightweight running shoes with cushioned sole, breathable mesh upper, suitable for marathon training."),
        (7,  "Yoga Mat",            "Sports",       1200,  500, "Non-slip eco-friendly yoga mat, 6mm thick, with carrying strap. Ideal for yoga and pilates."),
        (8,  "Coffee Maker",        "Appliances",   5800,  80,  "Drip coffee maker with 12-cup capacity, programmable timer, and keep-warm function."),
        (9,  "Mechanical Keyboard", "Electronics",  6500,  150, "Tenkeyless mechanical keyboard with Cherry MX Red switches, RGB backlight, and USB-C."),
        (10, "Office Chair",        "Furniture",    12000, 60,  "Ergonomic office chair with lumbar support, adjustable armrests, and mesh back. Ideal for long work hours."),
    ])

    # Customers table
    cursor.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            customer_name TEXT,
            city TEXT,
            email TEXT,
            total_orders INTEGER,
            total_spent REAL,
            notes TEXT
        )
    """)
    cursor.executemany("INSERT INTO customers VALUES (?,?,?,?,?,?,?)", [
        (101, "Rahul Sharma",   "Mumbai",    "rahul@example.com",  5, 150000, "Premium customer, prefers electronics. Has bought laptop and phone."),
        (102, "Priya Singh",    "Delhi",     "priya@example.com",  3, 85000,  "Regular customer, mostly buys appliances. Interested in kitchen products."),
        (103, "Amit Patel",     "Ahmedabad", "amit@example.com",   7, 210000, "High-value customer. Buys across all categories. Eligible for loyalty discount."),
        (104, "Sneha Reddy",    "Hyderabad", "sneha@example.com",  2, 40000,  "New customer, bought sports equipment. Interested in outdoor activities."),
        (105, "Vikram Nair",    "Bangalore", "vikram@example.com", 4, 95000,  "Tech enthusiast. Frequently buys electronics and accessories."),
        (106, "Anita Joshi",    "Pune",      "anita@example.com",  1, 12000,  "First-time customer. Bought furniture. Needs follow-up for review."),
        (107, "Rajesh Kumar",   "Chennai",   "rajesh@example.com", 6, 175000, "Loyal customer since 2022. Prefers premium products. Birthday in March."),
    ])

    # Orders table
    cursor.execute("""
        CREATE TABLE orders (
            order_id TEXT PRIMARY KEY,
            customer_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            amount REAL,
            status TEXT,
            order_date TEXT,
            delivery_date TEXT
        )
    """)
    cursor.executemany("INSERT INTO orders VALUES (?,?,?,?,?,?,?,?)", [
        ("ORD001", 101, 1,  1, 75000, "Delivered", "2024-01-15", "2024-01-20"),
        ("ORD002", 102, 4,  1, 28000, "Delivered", "2024-01-18", "2024-01-25"),
        ("ORD003", 103, 3,  1, 35000, "Delivered", "2024-02-01", "2024-02-05"),
        ("ORD004", 101, 3,  1, 35000, "Delivered", "2024-02-10", "2024-02-14"),
        ("ORD005", 105, 9,  1, 6500,  "Delivered", "2024-02-15", "2024-02-18"),
        ("ORD006", 104, 6,  2, 9000,  "Delivered", "2024-02-20", "2024-02-24"),
        ("ORD007", 103, 5,  1, 42000, "Shipped",   "2024-03-01", None),
        ("ORD008", 102, 8,  1, 5800,  "Shipped",   "2024-03-05", None),
        ("ORD009", 107, 1,  1, 75000, "Processing","2024-03-10", None),
        ("ORD010", 106, 10, 1, 12000, "Delivered", "2024-03-12", "2024-03-17"),
        ("ORD011", 103, 2,  1, 3500,  "Delivered", "2024-03-14", "2024-03-16"),
        ("ORD012", 105, 1,  1, 75000, "Processing","2024-03-18", None),
    ])

    conn.commit()
    conn.close()
    print(f"✅ Sample database created: {DB_PATH}")
    print("   Tables: products (10 rows), customers (7 rows), orders (12 rows)")


if __name__ == "__main__":
    create_sample_db()
