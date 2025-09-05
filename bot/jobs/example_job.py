from aiogram import Bot
from bot.helpers.date_time import DateAndTimeHelper


class EverydayJob:
    @staticmethod
    async def start(bot: Bot):
        """
        Просто пример фоновой задачи
        """
        now = DateAndTimeHelper.get_current_utc_time()