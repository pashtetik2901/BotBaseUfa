from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.jobs.example_job import EverydayJob

scheduler = AsyncIOScheduler()

async def start_jobs(bot: Bot):
    """
    Запускает все фоновые задачи.
    """
    # Пример постановки задачи в очередь
    scheduler.add_job(EverydayJob.start, "interval", seconds=300, kwargs={"bot": bot})

    scheduler.start()

