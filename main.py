import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F

from handler import router




BOT_TOKEN = os.getenv('BOT_TOKEN')

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)


async def main():
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.close()

# Запуск бота
if __name__ == '__main__':
    logging.info("Бот запущен и готов к отправке сообщений.")
    asyncio.run(main())
