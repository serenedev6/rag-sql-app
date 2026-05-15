import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def create_sample_tables():
    """Create sample tables in PostgreSQL RDS"""
    
    # Connect to RDS
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        port=os.getenv('DB_PORT', '5432')
    )
    
    cursor = conn.cursor()
    
    # Drop tables if they exist
    print("🗑️  Dropping existing tables...")
    cursor.execute("DROP TABLE IF EXISTS orders CASCADE")
    cursor.execute("DROP TABLE IF EXISTS customers CASCADE")
    cursor.execute("DROP TABLE IF EXISTS products CASCADE")
    
    # Products table
    print("📦 Creating products table...")
    cursor.execute("""
        CREATE TABLE products (
            id SERIAL PRIMARY KEY,
            product_name TEXT,
            category TEXT,
            price REAL,
            stock INTEGER,
            description TEXT
        )
    """)
    
    products_data = [
        ("Laptop Pro 15",       "Electronics",  75000, 50,  "High performance laptop with 16GB RAM, 512GB SSD, Intel i7 processor. Great for developers and designers."),
        ("Wireless Headphones", "Electronics",  3500,  200, "Noise-cancelling over-ear headphones with 30-hour battery life and Bluetooth 5.0."),
        ("Smartphone X12",      "Electronics",  35000, 120, "Latest flagship smartphone with 5G support, 108MP camera, and 6.7-inch AMOLED display."),
        ("Washing Machine 7kg", "Appliances",   28000, 30,  "Fully automatic front load washing machine with 15 wash programs and energy star rating."),
        ("Refrigerator 350L",   "Appliances",   42000, 25,  "Double door frost-free refrigerator with inverter compressor and vegetable crisper."),
        ("Running Shoes",       "Sports",       4500,  300, "Lightweight running shoes with cushioned sole, breathable mesh upper, suitable for marathon training."),
        ("Yoga Mat",            "Sports",       1200,  500, "Non-slip eco-friendly yoga mat, 6mm thick, with carrying strap. Ideal for yoga and pilates."),
        ("Coffee Maker",        "Appliances",   5800,  80,  "Drip coffee maker with 12-cup capacity, programmable timer, and keep-warm function."),
        ("Mechanical Keyboard", "Electronics",  6500,  150, "Tenkeyless mechanical keyboard with Cherry MX Red switches, RGB backlight, and USB-C."),
        ("Office Chair",        "Furniture",    12000, 60,  "Ergonomic office chair with lumbar support, adjustable armrests, and mesh back. Ideal for long work hours."),
    ]
    
    cursor.executemany(
        "INSERT INTO products (product_name, category, price, stock, description) VALUES (%s, %s, %s, %s, %s)",
        products_data
    )
    print(f"   ✅ Inserted {len(products_data)} products")
    
    # Customers table
    print("👥 Creating customers table...")
    cursor.execute("""
        CREATE TABLE customers (
            id SERIAL PRIMARY KEY,
            customer_name TEXT,
            city TEXT,
            email TEXT,
            total_orders INTEGER,
            total_spent REAL,
            notes TEXT
        )
    """)
    
    customers_data = [
        ("Rahul Sharma",   "Mumbai",    "rahul@example.com",  5, 150000, "Premium customer, prefers electronics. Has bought laptop and phone."),
        ("Priya Singh",    "Delhi",     "priya@example.com",  3, 85000,  "Regular customer, mostly buys appliances. Interested in kitchen products."),
        ("Amit Patel",     "Ahmedabad", "amit@example.com",   7, 210000, "High-value customer. Buys across all categories. Eligible for loyalty discount."),
        ("Sneha Reddy",    "Hyderabad", "sneha@example.com",  2, 40000,  "New customer, bought sports equipment. Interested in outdoor activities."),
        ("Vikram Nair",    "Bangalore", "vikram@example.com", 4, 95000,  "Tech enthusiast. Frequently buys electronics and accessories."),
        ("Anita Joshi",    "Pune",      "anita@example.com",  1, 12000,  "First-time customer. Bought furniture. Needs follow-up for review."),
        ("Rajesh Kumar",   "Chennai",   "rajesh@example.com", 6, 175000, "Loyal customer since 2022. Prefers premium products. Birthday in March."),
    ]
    
    cursor.executemany(
        "INSERT INTO customers (customer_name, city, email, total_orders, total_spent, notes) VALUES (%s, %s, %s, %s, %s, %s)",
        customers_data
    )
    print(f"   ✅ Inserted {len(customers_data)} customers")
    
    # Orders table
    print("📋 Creating orders table...")
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
    
    orders_data = [
        ("ORD001", 1, 1,  1, 75000, "Delivered", "2024-01-15", "2024-01-20"),
        ("ORD002", 2, 4,  1, 28000, "Delivered", "2024-01-18", "2024-01-25"),
        ("ORD003", 3, 3,  1, 35000, "Delivered", "2024-02-01", "2024-02-05"),
        ("ORD004", 1, 3,  1, 35000, "Delivered", "2024-02-10", "2024-02-14"),
        ("ORD005", 5, 9,  1, 6500,  "Delivered", "2024-02-15", "2024-02-18"),
        ("ORD006", 4, 6,  2, 9000,  "Delivered", "2024-02-20", "2024-02-24"),
        ("ORD007", 3, 5,  1, 42000, "Shipped",   "2024-03-01", None),
        ("ORD008", 2, 8,  1, 5800,  "Shipped",   "2024-03-05", None),
        ("ORD009", 7, 1,  1, 75000, "Processing","2024-03-10", None),
        ("ORD010", 6, 10, 1, 12000, "Delivered", "2024-03-12", "2024-03-17"),
        ("ORD011", 3, 2,  1, 3500,  "Delivered", "2024-03-14", "2024-03-16"),
        ("ORD012", 5, 1,  1, 75000, "Processing","2024-03-18", None),
    ]
    
    cursor.executemany(
        "INSERT INTO orders (order_id, customer_id, product_id, quantity, amount, status, order_date, delivery_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        orders_data
    )
    print(f"   ✅ Inserted {len(orders_data)} orders")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n🎉 Sample database created successfully!")
    print("   Tables: products (10 rows), customers (7 rows), orders (12 rows)")


if __name__ == "__main__":
    create_sample_tables()