import sqlite3
from datetime import datetime

def get_db_connection():
    conn = sqlite3.connect('lostfound.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect('lostfound.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            reg_number TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'student',
            is_deleted BOOLEAN DEFAULT 0 
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lost_ids (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, 
            student_name TEXT NOT NULL,
            reg_number TEXT NOT NULL,
            department TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            image_path TEXT NOT NULL,
            date_reported DATETIME,
            status TEXT DEFAULT 'Lost',
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS found_ids (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, 
            location_found TEXT NOT NULL,
            image_path TEXT NOT NULL,
            date_reported DATETIME,
            extracted_name TEXT,
            extracted_reg_number TEXT,
            extracted_department TEXT,
            extracted_phone TEXT,
            status TEXT DEFAULT 'Unclaimed',
            claimed_by_user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            found_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            claim_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Pending',
            date_claimed TEXT DEFAULT CURRENT_TIMESTAMP,
            admin_notes TEXT,
            FOREIGN KEY(found_id) REFERENCES found_ids(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized.")

def get_lost_ids(limit=8, offset=0):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT student_name, reg_number, department, image_path, date_reported 
        FROM lost_ids 
        WHERE status = 'Lost'
        ORDER BY date_reported DESC
        LIMIT ? OFFSET ?
    """, (limit, offset))

    records = cursor.fetchall()
    conn.close()
    return [dict(row) for row in records]

def get_found_ids(limit=8, offset=0):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, location_found, image_path, date_reported 
        FROM found_ids 
        WHERE status = 'Unclaimed'
        ORDER BY date_reported DESC
        LIMIT ? OFFSET ?
    """, (limit, offset))

    records = cursor.fetchall()
    conn.close()
    return [dict(row) for row in records]