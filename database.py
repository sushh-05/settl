import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'app.db')

def get_db_connection():
    """Establish and return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database and create tables if they don't exist."""
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Businesses Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS businesses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_name TEXT NOT NULL,
            owner_name TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. Buyers Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS buyers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_id INTEGER,
            buyer_name TEXT NOT NULL,
            contact_person TEXT,
            phone TEXT,
            email TEXT,
            payment_terms_days INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (business_id) REFERENCES businesses (id)
        )
    ''')

    # 3. Invoices Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            buyer_id INTEGER,
            invoice_number TEXT NOT NULL,
            invoice_date DATE,
            due_date DATE,
            invoice_amount REAL NOT NULL,
            amount_paid REAL DEFAULT 0.0,
            balance_due REAL NOT NULL,
            status TEXT DEFAULT 'Pending',
            document_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (buyer_id) REFERENCES buyers (id)
        )
    ''')

    # 4. Payments Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER,
            amount REAL NOT NULL,
            payment_date DATE,
            payment_mode TEXT,
            reference_number TEXT,
            notes TEXT,
            FOREIGN KEY (invoice_id) REFERENCES invoices (id)
        )
    ''')

    # 5. Reminders Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER,
            reminder_type TEXT,
            message TEXT,
            sent_date TIMESTAMP,
            channel TEXT,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (invoice_id) REFERENCES invoices (id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database tables created successfully.")
