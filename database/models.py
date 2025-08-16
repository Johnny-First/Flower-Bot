import aiosqlite

DB_PATH = 'users.db'
 
async def create_all_tables():
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                cart_price INTEGER DEFAULT 0,
                cart_items TEXT DEFAULT '[]'
            )
        ''')
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL
            )
        ''')
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS flowers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                caption TEXT,
                photo_id TEXT NOT NULL,
                category_id INTEGER NOT NULL
            )
        ''')
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                in_stock INTEGER
            )
        ''')
        await conn.commit()

async def get_history(user_id, limit=10):
    async with aiosqlite.connect(DB_PATH) as conn:
        async with conn.execute(
            "SELECT role, content FROM messages WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (user_id, limit)
        ) as cursor:
            rows = await cursor.fetchall()
    return [{"role": role, "content": content} for role, content in reversed(rows)]

async def add_message(user_id: int, role: str, message: str):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            'INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)',
            (user_id, role, message)
        )
        await conn.commit()

async def add_user(user_id: int, username: str, first_name: str, last_name: str):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            'INSERT OR IGNORE INTO users (user_id, username, first_name, last_name) VALUES (?, ?, ?, ?)',
            (user_id, username, first_name, last_name)
        )
        await conn.commit()

async def add_category(name: str, in_stock: int = 1):
    try:
        async with aiosqlite.connect(DB_PATH) as conn:
            await conn.execute(
                'INSERT INTO categories (name, in_stock) VALUES (?, ?)',
                (name, in_stock)
            )
            await conn.commit()
    except Exception as e:
        print(f"Ошибка в add_category: {e}")  

async def add_flower(name: str, caption: str, photo_id: str, category_id: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            'INSERT INTO flowers (name, caption, photo_id, category_id) VALUES (?, ?, ?, ?)',
            (name, caption, photo_id, category_id)
        )
        await conn.commit()

async def delete_category(category_id: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            'DELETE FROM categories WHERE id = ?',
            (category_id,)
        )
        await conn.commit()

async def delete_flower(flower_id: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            'DELETE FROM flowers WHERE id = ?',
            (flower_id,)
        )
        await conn.commit()
         

async def get_media_flower(flower_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        async with conn.execute('SELECT name, caption, photo_id FROM flowers WHERE id = ?', 
                                (flower_id)) as cursor:
            flowers = await cursor.fetchone()
    return flowers

async def get_flower_category(flower_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        async with conn.execute('SELECT category_id FROM flowers WHERE id = ?', 
                                (flower_id)) as cursor:
            category = await cursor.fetchone()
    return category[0]
