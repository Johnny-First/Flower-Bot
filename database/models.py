import sqlite3

DB_PATH = 'users.db'

def create_messages_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def get_history(user_id, limit=10):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute(
        "SELECT role, content FROM messages WHERE user_id=? ORDER BY id DESC LIMIT ?",
        (user_id, limit)
    )
    rows = c.fetchall()
    conn.close()
    # Переворачиваем, чтобы сообщения шли в хронологическом порядке (от старых к новым)
    return [{"role": role, "content": content} for role, content in reversed(rows)]

def add_message(user_id: int, role: str, message: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)
    ''', (user_id, role, message))
    conn.commit()
    conn.close()

def create_flowers_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flowers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            caption TEXT,
            photo_id TEXT NOT NULL,
            heritage TEXT NOT NULL,
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
