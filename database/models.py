import aiosqlite

DB_PATH = 'users.db'
 
class DatabaseManager:
    """Основной класс для управления базой данных"""
    
    @staticmethod
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
                    photo_id TEXT,
                    in_stock BOOLEAN NOT NULL DEFAULT 1
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS checkout (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    phone TEXT NOT NULL,
                    customer_name TEXT NOT NULL,
                    cart_items TEXT NOT NULL,
                    total_price DECIMAL(10, 2) NOT NULL,
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending'
                )
            ''')
            await conn.commit()


class UserManager:
    """Класс для управления пользователями"""
    
    @staticmethod
    async def add_user(user_id: int, username: str, first_name: str, last_name: str):
        """Добавление нового пользователя"""
        async with aiosqlite.connect(DB_PATH) as conn:
            await conn.execute(
                'INSERT OR IGNORE INTO users (user_id, username, first_name, last_name) VALUES (?, ?, ?, ?)',
                (user_id, username, first_name, last_name)
            )
            await conn.commit()
    
    @staticmethod
    async def get_cart(user_id: int):
        """Получение корзины пользователя"""
        try:
            async with aiosqlite.connect(DB_PATH) as conn:
                async with conn.execute(
                    'SELECT cart_items, cart_price FROM users WHERE user_id = ?',
                    (user_id,)
                ) as cursor:
                    result = await cursor.fetchone()
                
                if not result or not result[0]:
                    # Корзина пуста
                    return {
                        'items': [],
                        'total_price': 0
                    }
                
                cart_items = result[0]
                total_price = result[1] or 0
                
                # Парсим JSON корзины
                try:
                    import json
                    items = json.loads(cart_items)
                    return {
                        'items': items,
                        'total_price': total_price
                    }
                except json.JSONDecodeError:
                    # Если JSON поврежден, возвращаем пустую корзину
                    return {
                        'items': [],
                        'total_price': 0
                    }
                    
        except Exception as e:
            print(f"Ошибка при получении корзины: {e}")
            return {
                'items': [],
                'total_price': 0
            }
    
    @staticmethod
    async def to_cart(user_id: int, new_item: dict):
        """Добавление товара в корзину пользователя"""
        try:
            import json
            
            async with aiosqlite.connect(DB_PATH) as conn:
                flower_id = new_item.get('id')
                quantity = new_item.get('quantity', 1)
                
                async with conn.execute(
                    'SELECT name, price FROM flowers WHERE id = ?',
                    (flower_id,)
                ) as cursor:
                    flower_info = await cursor.fetchone()
                
                if not flower_info:
                    raise ValueError(f"Товар с id {flower_id} не найден")
                
                flower_name, flower_price = flower_info
                
                async with conn.execute(
                    'SELECT cart_items, cart_price FROM users WHERE user_id = ?',
                    (user_id,)
                ) as cursor:
                    result = await cursor.fetchone()
                
                if result:
                    current_cart_items = result[0] or '[]'
                    current_cart_price = result[1] or 0
                    
                    try:
                        current_cart = json.loads(current_cart_items)
                    except json.JSONDecodeError:
                        current_cart = []
                else:
                    current_cart = []
                    current_cart_price = 0
                
                item_found = False
                for existing_item in current_cart:
                    if existing_item.get('id') == flower_id:
                        existing_item['quantity'] = quantity
                        item_found = True
                        break
                
                if not item_found:
                    current_cart.append({
                        'id': flower_id,
                        'name': flower_name,
                        'price': flower_price,
                        'quantity': quantity
                    })
                
                total_price = 0
                for item in current_cart:
                    if 'quantity' in item and 'price' in item:
                        total_price += item['quantity'] * item['price']
                
                updated_cart_json = json.dumps(current_cart)
                
                await conn.execute(
                    '''UPDATE users 
                    SET cart_items = ?, cart_price = ? 
                    WHERE user_id = ?''',
                    (updated_cart_json, total_price, user_id)
                )
                await conn.commit()

        except Exception as e:
            print(f"Ошибка при обновлении корзины: {e}")
            raise e

    @staticmethod
    async def clear_cart(user_id: int):
        """Очистка корзины пользователя"""
        try:
            async with aiosqlite.connect(DB_PATH) as conn:
                await conn.execute(
                    '''UPDATE users 
                    SET cart_items = '[]', cart_price = 0 
                    WHERE user_id = ?''',
                    (user_id,)
                )
                await conn.commit()
                return True
        except Exception as e:
            print(f"Ошибка при очистке корзины: {e}")
            return False


class MessageManager:
    """Класс для управления сообщениями"""
    
    @staticmethod
    async def add_message(user_id: int, role: str, message: str):
        """Добавление нового сообщения"""
        async with aiosqlite.connect(DB_PATH) as conn:
            await conn.execute(
                'INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)',
                (user_id, role, message)
            )
            await conn.commit()

    @staticmethod
    async def get_history(user_id, limit=10):
        """Получение истории сообщений пользователя"""
        async with aiosqlite.connect(DB_PATH) as conn:
            async with conn.execute(
                "SELECT role, content FROM messages WHERE user_id=? ORDER BY id DESC LIMIT ?",
                (user_id, limit)
            ) as cursor:
                rows = await cursor.fetchall()
        return [{"role": role, "content": content} for role, content in reversed(rows)]


class CategoryManager:
    """Класс для управления категориями"""
    
    @staticmethod
    async def add_category(name: str, photo_id: str = None, in_stock: int = 1):
        """Добавление новой категории"""
        try:
            async with aiosqlite.connect(DB_PATH) as conn:
                await conn.execute(
                    '''INSERT INTO categories (name, photo_id, in_stock) 
                    VALUES (?, ?, ?) 
                    ON CONFLICT(name) 
                        DO UPDATE SET photo_id = excluded.photo_id, in_stock = excluded.in_stock;''',
                    (name, photo_id, in_stock)
                )
                await conn.commit()
        except Exception as e:
            print(f"Ошибка в add_category: {e}")  
            raise e
    
    @staticmethod
    async def delete_category(category_id: int):
        """Удаление категории и всех цветов в ней"""
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

    @staticmethod
    async def get_all_categories():
        """Получить все категории для админ-панели"""
        async with aiosqlite.connect(DB_PATH) as conn:
            async with conn.execute('SELECT name, id, in_stock FROM categories') as cursor:
                categories = await cursor.fetchall()
        return categories
    
    @staticmethod
    async def get_available_categories():
        """Получить только доступные категории (in_stock = 1)"""
        async with aiosqlite.connect(DB_PATH) as conn:
            async with conn.execute('SELECT name, id FROM categories WHERE in_stock = 1') as cursor:
                categories = await cursor.fetchall()
        return categories

    @staticmethod
    async def get_category_photo(category_id: int):
        """Получение фотографии категории"""
        async with aiosqlite.connect(DB_PATH) as conn:
            async with conn.execute('SELECT photo_id FROM categories WHERE id = ?', 
                                    (category_id,)) as cursor:
                result = await cursor.fetchone()
        return result[0] if result else None


class FlowerManager:
    """Класс для управления цветами"""
    
    @staticmethod
    async def add_flower(name: str, price: str, caption: str, photo_id: str, category_id: int):
        """Добавление нового цветка"""
        async with aiosqlite.connect(DB_PATH) as conn:
            await conn.execute(
                'INSERT INTO flowers (name, price, caption, photo_id, category_id) VALUES (?, ?, ?, ?, ?)',
                (name, price, caption, photo_id, category_id)
            )
            await conn.commit()
    
    @staticmethod
    async def delete_flower(flower_id: int):
        """Удаление цветка"""
        async with aiosqlite.connect(DB_PATH) as conn:
            await conn.execute(
                'DELETE FROM flowers WHERE id = ?',
                (flower_id,)
            )
            await conn.commit()
         
    @staticmethod
    async def get_media_flower(flower_id):
        """Получение информации о цветке для медиа"""
        async with aiosqlite.connect(DB_PATH) as conn:
            async with conn.execute('SELECT name, caption, photo_id FROM flowers WHERE id = ?', 
                                    (flower_id,)) as cursor:
                flowers = await cursor.fetchone()
        return flowers

    @staticmethod
    async def get_flower_category(flower_id):
        """Получение категории цветка"""
        async with aiosqlite.connect(DB_PATH) as conn:
            async with conn.execute('SELECT category_id FROM flowers WHERE id = ?', 
                                    (flower_id,)) as cursor:
                category = await cursor.fetchone()
        return category[0] if category else None

    @staticmethod
    async def get_flower_stock(flower_id):
        """Получение статуса наличия цветка"""
        async with aiosqlite.connect(DB_PATH) as conn:
            async with conn.execute('SELECT in_stock FROM flowers WHERE id = ?', 
                                    (flower_id,)) as cursor:
                stock = await cursor.fetchone()
        return stock[0] if stock else None
    
    @staticmethod
    async def stop_flower(flower_id):
        """Переключение статуса наличия цветка"""
        async with aiosqlite.connect(DB_PATH) as conn:
            await conn.execute('UPDATE flowers SET in_stock = NOT in_stock WHERE id = ?', (flower_id,))
            await conn.commit()

    @staticmethod
    async def get_flowers_by_category(category_id: int):
        """Получить все цветы в определенной категории"""
        async with aiosqlite.connect(DB_PATH) as conn:
            async with conn.execute('SELECT * FROM flowers WHERE category_id = ?', (category_id,)) as cursor:
                flowers = await cursor.fetchall()
        return flowers


class CheckoutManager:
    """Класс для управления заказами"""
    
    @staticmethod
    async def create_order(user_id: int, username: str, first_name: str, last_name: str, phone: str, customer_name: str, cart_items: str, total_price: float):
        """Создание нового заказа"""
        async with aiosqlite.connect(DB_PATH) as conn:
            await conn.execute(
                'INSERT INTO checkout (user_id, username, first_name, last_name, phone, customer_name, cart_items, total_price) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (user_id, username, first_name, last_name, phone, customer_name, cart_items, total_price)
            )
            await conn.commit()
    
    @staticmethod
    async def get_orders_by_user(user_id: int):
        """Получение заказов пользователя"""
        async with aiosqlite.connect(DB_PATH) as conn:
            async with conn.execute(
                'SELECT * FROM checkout WHERE user_id = ? ORDER BY order_date DESC',
                (user_id,)
            ) as cursor:
                orders = await cursor.fetchall()
        return orders

    @staticmethod
    async def get_all_orders():
        """Получение всех заказов для админ-панели"""
        async with aiosqlite.connect(DB_PATH) as conn:
            async with conn.execute('SELECT * FROM checkout ORDER BY order_date DESC') as cursor:
                orders = await cursor.fetchall()
        return orders
    
    @staticmethod
    async def update_order_status(order_id: int, status: str):
        """Обновление статуса заказа"""
        async with aiosqlite.connect(DB_PATH) as conn:
            await conn.execute(
                'UPDATE checkout SET status = ? WHERE id = ?',
                (status, order_id)
            )
            await conn.commit()


# Функции-алиасы для обратной совместимости
async def create_all_tables():
    """Алиас для DatabaseManager.create_all_tables"""
    return await DatabaseManager.create_all_tables()

async def add_user(user_id: int, username: str, first_name: str, last_name: str):
    """Алиас для UserManager.add_user"""
    return await UserManager.add_user(user_id, username, first_name, last_name)

async def get_cart(user_id: int):
    """Алиас для UserManager.get_cart"""
    return await UserManager.get_cart(user_id)

async def to_cart(user_id: int, new_item: dict):
    """Алиас для UserManager.to_cart"""
    return await UserManager.to_cart(user_id, new_item)

async def clear_cart(user_id: int):
    """Алиас для UserManager.clear_cart"""
    return await UserManager.clear_cart(user_id)

async def add_message(user_id: int, role: str, message: str):
    """Алиас для MessageManager.add_message"""
    return await MessageManager.add_message(user_id, role, message)

async def get_history(user_id, limit=10):
    """Алиас для MessageManager.get_history"""
    return await MessageManager.get_history(user_id, limit)

async def add_category(name: str, photo_id: str = None, in_stock: int = 1):
    """Алиас для CategoryManager.add_category"""
    return await CategoryManager.add_category(name, photo_id, in_stock)

async def delete_category(category_id: int):
    """Алиас для CategoryManager.delete_category"""
    return await CategoryManager.delete_category(category_id)

async def get_all_categories():
    """Алиас для CategoryManager.get_all_categories"""
    return await CategoryManager.get_all_categories()

async def get_available_categories():
    """Алиас для CategoryManager.get_available_categories"""
    return await CategoryManager.get_available_categories()

async def get_category_photo(category_id: int):
    """Алиас для CategoryManager.get_category_photo"""
    return await CategoryManager.get_category_photo(category_id)

async def add_flower(name: str, price: str, caption: str, photo_id: str, category_id: int):
    """Алиас для FlowerManager.add_flower"""
    return await FlowerManager.add_flower(name, price, caption, photo_id, category_id)

async def delete_flower(flower_id: int):
    """Алиас для FlowerManager.delete_flower"""
    return await FlowerManager.delete_flower(flower_id)

async def get_media_flower(flower_id):
    """Алиас для FlowerManager.get_media_flower"""
    return await FlowerManager.get_media_flower(flower_id)

async def get_flower_category(flower_id):
    """Алиас для FlowerManager.get_flower_category"""
    return await FlowerManager.get_flower_category(flower_id)

async def get_flower_stock(flower_id):
    """Алиас для FlowerManager.get_flower_stock"""
    return await FlowerManager.get_flower_stock(flower_id)

async def stop_flower(flower_id):
    """Алиас для FlowerManager.stop_flower"""
    return await FlowerManager.stop_flower(flower_id)

async def get_flowers_by_category(category_id: int):
    """Алиас для FlowerManager.get_flowers_by_category"""
    return await FlowerManager.get_flowers_by_category(category_id)

async def create_order(user_id: int, username: str, first_name: str, last_name: str, phone: str, customer_name: str, cart_items: str, total_price: float):
    """Алиас для CheckoutManager.create_order"""
    return await CheckoutManager.create_order(user_id, username, first_name, last_name, phone, customer_name, cart_items, total_price)

async def get_orders_by_user(user_id: int):
    """Алиас для CheckoutManager.get_orders_by_user"""
    return await CheckoutManager.get_orders_by_user(user_id)

async def get_all_orders():
    """Алиас для CheckoutManager.get_all_orders"""
    return await CheckoutManager.get_all_orders()

async def update_order_status(order_id: int, status: str):
    """Алиас для CheckoutManager.update_order_status"""
    return await CheckoutManager.update_order_status(order_id, status) 