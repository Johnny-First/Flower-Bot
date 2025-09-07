#!/usr/bin/env python3
"""
Тест импортов для проверки работоспособности проекта
"""

def test_imports():
    """Тестируем все основные импорты"""
    try:
        print("🔍 Тестирование импортов...")
        
        # Тест основных модулей
        print("  📦 Тестируем config...")
        from config import settings
        print(f"    ✅ settings загружен: {type(settings)}")
        
        print("  📦 Тестируем database...")
        from database.models import create_all_tables
        print("    ✅ database.models загружен")
        
        print("  📦 Тестируем handlers...")
        from handlers import BaseHandlers, FlowerHandlers, AdminHandlers, PaymentHandlers, AI_Handlers
        print("    ✅ handlers загружены")
        
        print("  📦 Тестируем services...")
        from services.ai import AI_GPT
        print("    ✅ services.ai загружен")
        
        print("  📦 Тестируем keyboards...")
        from config.keyboards import get_base_keyboard
        print("    ✅ keyboards загружены")
        
        print("\n✅ Все импорты успешны!")
        return True
        
    except ImportError as e:
        print(f"\n❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        return False

def test_settings():
    """Тестируем настройки"""
    try:
        print("\n🔧 Тестирование настроек...")
        from config import settings
        
        # Проверяем, что настройки загружаются (даже если значения None)
        attrs = ['BOT_TOKEN', 'DEEP_KEY', 'PAYMENT_TOKEN', 'CHANNEL_URL', 'API_KEY', 'ADMIN_IDS']
        
        for attr in attrs:
            value = getattr(settings, attr, None)
            print(f"  {attr}: {'✅' if value else '⚠️  (не задано)'}")
        
        print("✅ Настройки загружены")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка настроек: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск тестов работоспособности проекта...\n")
    
    success = True
    success &= test_imports()
    success &= test_settings()
    
    if success:
        print("\n🎉 Проект готов к работе!")
        print("📝 Не забудьте создать файл .env с необходимыми переменными:")
        print("   BOT_TOKEN, DEEP_KEY, PAYMENT_TOKEN, CHANNEL_URL, API_KEY, ADMIN_IDS")
    else:
        print("\n💥 Обнаружены проблемы, требующие исправления")
