import os
import uuid

from aiogram import Bot
from aiogram.types import PhotoSize

from bot.config import BASE_DIR

MEDIA_DIR = os.path.join(BASE_DIR, "media")

class FileHelper:

    @staticmethod
    def save_file(file_bytes: bytes, file_extension: str) -> str:
        """
        Сохраняет файл на диск и возвращает относительный путь к файлу.
        :param file_bytes: Байты файла.
        :param file_extension: Расширение файла (например, ".jpg").
        :return: Относительный путь к файлу.
        """
        # Генерируем уникальное имя файла
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(MEDIA_DIR, unique_filename)

        # Создаем директорию, если её нет
        os.makedirs(MEDIA_DIR, exist_ok=True)

        # Сохраняем файл на диск
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        return unique_filename

    @staticmethod
    async def download_photo(bot: Bot, photo: PhotoSize) -> str:
        """
        Скачивает фото и сохраняет его в папку MEDIA_DIR.
        Возвращает относительный путь к файлу.
        """
        # Создаем папку, если её нет
        os.makedirs(MEDIA_DIR, exist_ok=True)

        # Генерируем имя файла на основе file_id
        file_extension = ".jpg"  # Фото обычно в формате JPEG
        file_name = f"{photo.file_id}{file_extension}"
        file_path = os.path.join(MEDIA_DIR, file_name)

        # Скачиваем файл
        file_info = await bot.get_file(photo.file_id)
        await bot.download_file(file_info.file_path, file_path)

        # Возвращаем имя файла
        return file_name