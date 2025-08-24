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
                price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
                caption TEXT,
                photo_id TEXT NOT NULL,
                category_id INTEGER NOT NULL,
                in_stock BOOLEAN NOT NULL DEFAULT 1
            )
        ''')
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            in_stock BOOLEAN NOT NULL DEFAULT 1
        );
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
                '''INSERT INTO categories (name, in_stock) 
            VALUES (?, ?) 
            ON CONFLICT(name) 
            DO UPDATE SET in_stock = excluded.in_stock;''',
            (name, in_stock)
            )
            await conn.commit()
    except Exception as e:
        print(f"Ошибка в add_category: {e}")  

async def add_flower(name: str, price: str, caption: str, photo_id: str, category_id: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            'INSERT INTO flowers (name, price, caption, photo_id, category_id) VALUES (?, ?, ?, ?, ?)',
            (name, price, caption, photo_id, category_id)
        )
        await conn.commit()

async def delete_category(category_id: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            'DELETE FROM categories WHERE id = ?',
            (category_id,)
        )
        await conn.execute(
            'DELETE FROM flowers WHERE category_id = ?',
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

async def get_flower_stock(flower_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        async with conn.execute('SELECT in_stock FROM flowers WHERE id = ?', 
                                (flower_id)) as cursor:
            category = await cursor.fetchone()
    return category[0]

async def stop_flower(flower_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        async with conn.execute('UPDATE flowers SET in_stock = NOT in_stock WHERE id = ?', (flower_id,)) as cursor:
            await conn.commit()

async def get_all_categories():
    """Получить все категории для админ-панели"""
    async with aiosqlite.connect(DB_PATH) as conn:
        async with conn.execute('SELECT name, id, in_stock FROM categories') as cursor:
            categories = await cursor.fetchall()
    return categories

async def get_available_categories():
    """Получить только доступные категории (in_stock = 1)"""
    async with aiosqlite.connect(DB_PATH) as conn:
        async with conn.execute('SELECT name, id FROM categories WHERE in_stock = 1') as cursor:
            categories = await cursor.fetchall()
    return categories


async def get_flowers_by_category(category_id: int):
    """Получить все цветы в определенной категории"""
    async with aiosqlite.connect(DB_PATH) as conn:
        async with conn.execute('SELECT * FROM flowers WHERE category_id = ?', (category_id,)) as cursor:
            flowers = await cursor.fetchall()
    return flowers
