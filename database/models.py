import sqlite3

DB_PATH = 'users.db'

def create_flowers_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flowers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            caption TEXT,
            photo_id TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_flower(name: str, caption: str, photo_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO flowers (name, caption, photo_id) VALUES (?, ?, ?)
    ''', (name, caption, photo_id))
    conn.commit()
    conn.close()

def get_all_flowers():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, caption, photo_id FROM flowers')
    flowers = cursor.fetchall()
    conn.close()
    return flowers
