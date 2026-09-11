import database
from datetime import date, timedelta

def insert_fake_data():
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    # Check if data already exists
    cursor.execute("SELECT COUNT(*) as count FROM invoices")
    if cursor.fetchone()['count'] > 0:
        print("Data already exists. Skipping fake data insertion.")
        conn.close()
        return

    # 1. Create Business
    cursor.execute('''
        INSERT INTO businesses (business_name, owner_name, phone, email, address)
        VALUES ('Tech Solutions MSME', 'Rahul Sharma', '9876543210', 'rahul@techsolutions.com', '123 Tech Park, Bangalore')
    ''')
    
    # 2. Create Buyers
    buyers = [
        ('ABC Fabricators', 'Amit Kumar', '9988776655', 'amit@abcfab.com', 30),
        ('Ravi Traders', 'Ravi Singh', '9988776644', 'ravi@traders.com', 15),
        ('Kumar Works', 'Suresh Kumar', '9988776633', 'suresh@kumarworks.com', 45)
    ]
    
    for b in buyers:
        cursor.execute('''
            INSERT INTO buyers (buyer_name, contact_person, phone, email, payment_terms_days)
            VALUES (?, ?, ?, ?, ?)
        ''', b)
        
    # 3. Create Invoices
    today = date.today()
    
    invoices = [
        # INV-101 – ₹25,000 – Paid
        (1, 'INV-101', today - timedelta(days=40), today - timedelta(days=10), 25000.0, 25000.0, 0.0, 'Paid', None),
        
        # INV-102 – ₹48,000 – Partially paid
        (2, 'INV-102', today - timedelta(days=20), today + timedelta(days=10), 48000.0, 18000.0, 30000.0, 'Partially paid', None),
        
        # INV-103 – ₹12,500 – Due soon
        (3, 'INV-103', today - timedelta(days=5), today + timedelta(days=10), 12500.0, 0.0, 12500.0, 'Due', None),
        
        # INV-104 – ₹75,000 – Overdue
        (1, 'INV-104', today - timedelta(days=60), today - timedelta(days=30), 75000.0, 0.0, 75000.0, 'Overdue', None),
        
        # INV-105 – ₹18,000 – Overdue
        (2, 'INV-105', today - timedelta(days=45), today - timedelta(days=15), 18000.0, 0.0, 18000.0, 'Overdue', None)
    ]
    
    for inv in invoices:
        cursor.execute('''
            INSERT INTO invoices (buyer_id, invoice_number, invoice_date, due_date, invoice_amount, amount_paid, balance_due, status, document_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', inv)
        
    # 4. Create Payments
    payments = [
        # Full payment for INV-101
        (1, 25000.0, today - timedelta(days=15), 'Bank Transfer', 'TXN12345', 'Full payment received'),
        # Partial payment for INV-102
        (2, 18000.0, today - timedelta(days=5), 'UPI', 'UPI98765', 'Advance payment')
    ]
    
    for p in payments:
        cursor.execute('''
            INSERT INTO payments (invoice_id, amount, payment_date, payment_mode, reference_number, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', p)
        
    # 5. Create Reminders
    reminders = [
        # Reminder for INV-104
        (4, 'Friendly reminder', 'Just a friendly reminder...', today - timedelta(days=25), 'Manual', 'Sent'),
        (4, 'Overdue reminder', 'This is a notice...', today - timedelta(days=10), 'Manual', 'Sent')
    ]
    
    for r in reminders:
        cursor.execute('''
            INSERT INTO reminders (invoice_id, reminder_type, message, sent_date, channel, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', r)

    conn.commit()
    conn.close()
    print("Fake data inserted successfully.")

if __name__ == '__main__':
    insert_fake_data()
