DATABASE_FILE = "coffee_shop.db"
import sqlite3

def get_db_connection():
    """Establishes and returns a SQLite database connection."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row # This allows accessing columns by name
    return conn

# --- Database Initialization (Run this once to create tables and populate initial data) ---
def initialize_database():
    """Creates tables and populates initial data if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create menu_items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            available BOOLEAN NOT NULL DEFAULT 1
        )
    ''')

    # Create orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_session_id TEXT NOT NULL,
            order_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL DEFAULT 'pending',
            total_price REAL NOT NULL DEFAULT 0.0
        )
    ''')

    # Create order_items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            customizations TEXT,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (item_id) REFERENCES menu_items (id)
        )
    ''')

    # Insert initial data if menu_items table is empty
    cursor.execute("SELECT COUNT(*) FROM menu_items")
    if cursor.fetchone()[0] == 0:
        initial_items = [
            ('Latte', 'Hot Drinks', 18.00, 'Classic espresso with steamed milk and a thin layer of foam.', 1),
            ('Cappuccino', 'Hot Drinks', 18.00, 'Espresso with steamed milk and a thick layer of foam.', 1),
            ('Espresso', 'Hot Drinks', 12.00, 'A strong shot of coffee.', 1),
            ('Americano', 'Hot Drinks', 15.00, 'Espresso diluted with hot water.', 1),
            ('Iced Latte', 'Cold Drinks', 20.00, 'Espresso with cold milk and ice.', 1),
            ('Cold Brew', 'Cold Drinks', 22.00, 'Slow-steeped coffee concentrate over ice.', 1),
            ('Mocha', 'Hot Drinks', 20.00, 'Espresso with chocolate sauce and steamed milk.', 1),
            ('Croissant', 'Pastries', 10.00, 'Flaky, buttery pastry.', 1),
            ('Blueberry Muffin', 'Pastries', 12.00, 'Sweet muffin with fresh blueberries.', 1)
        ]
        cursor.executemany('''
            INSERT INTO menu_items (name, category, price, description, available)
            VALUES (?, ?, ?, ?, ?)
        ''', initial_items)
        conn.commit()
    conn.close()