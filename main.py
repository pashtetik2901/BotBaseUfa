import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.enums import ParseMode
from bot.config import Config
from bot.handlers import setup_handlers
from aiogram.client.default import DefaultBotProperties

# from config import Config
# from handlers import setup_handlers
# from jobs import scheduler, start_jobs

from bot.jobs import scheduler, start_jobs

from bot.utils.state import storage

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()          # Логирование в консоль
    ]
)

#Menu
commands = [
    BotCommand(command='start', description='Запуск/перезапуск'),
]

async def set_command(bot: Bot):
    await bot.set_my_commands(commands)

# Инициализация бота и диспетчера
bot = Bot(
    token=Config.TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=storage)

# Регистрация обработчиков
setup_handlers(dp)

# Запуск бота
async def main():
    try:
        logging.info("Бот запущен")

        if Config.SCHEDULER == True:
            # Запускаем планировщик задач
            await start_jobs(bot=bot)

        await set_command(bot)

        # Запускаем бота
        await dp.start_polling(bot, skip_updates=True)

    except Exception as e:
        logging.error(f"Ошибка запуска бота: {e}")

    finally:
        logging.info("Остановка планировщика задач...")
        if scheduler.running:  # Проверяем, запущен ли планировщик
            scheduler.shutdown(wait=False)  # Останавливаем планировщик без ожидания завершения задач
        logging.info("Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())