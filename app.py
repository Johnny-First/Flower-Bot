from aiogram import Bot, Dispatcher
import asyncio
from .config.settings import settings
from .handlers import ( 
    FlowerHandlers,
    BaseHandlers,
    # PaymentHandlers,
    AI_Handlers
)

async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    FlowerHandlers(dp)
    BaseHandlers(dp)
    # PaymentHandlers(dp)
    AI_Handlers(dp)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())