import os
from typing import Optional

import aiohttp
import pandas as pd
from io import BytesIO
from bot.config import Config, BASE_DIR

from bot.helpers.file_logger import CustomLogger

TMP_FILE_PATH = os.path.join(BASE_DIR, 'tmp_files')

class YandexDiskService:
    def __init__(self):
        self.api_base = "https://cloud-api.yandex.net/v1/disk"
        self.headers = {
            "Authorization": f"OAuth {Config.YANDEX_DISK_TOKEN}" if Config.YANDEX_DISK_TOKEN else "",
            "Content-Type": "application/json",
        }
        self.local_file_path = os.path.join(TMP_FILE_PATH, 'tmp_file.xlsx')
        if not os.path.exists(TMP_FILE_PATH):
            os.makedirs(TMP_FILE_PATH)

        self.logger = CustomLogger(source="yandex_disk", log_to_file=True, log_to_console=False)

    async def update_yandex_xlsx(self,
                                 sheet_name: Optional[str] = None,
                                 needle_column: Optional[str] = None,
                                 needle_value: Optional[str] = None,
                                 **kwargs,
                             ):
        """Обновляет Excel-файл на Яндекс.Диске."""
        result = None
        try:
            if not Config.YANDEX_DISK_TOKEN or not Config.YANDEX_DISK_FILE_PATH:
                raise ValueError("Токен или путь к файлу на Яндекс.Диске не указаны.")

            # Получаем ссылку для загрузки файла
            upload_url = await self.get_upload_link()
            if not upload_url:
                raise ValueError("Ошибка: Не удалось получить ссылку для загрузки файла.")

            file_path = await self.download_file()
            if not file_path:
                raise ValueError("Ошибка при скачивании файла.")

            file_result = await self.update_excel_file(
                file_path=file_path,
                sheet_name=sheet_name,
                needle_column=needle_column,
                needle_value=needle_value,
                **kwargs
            )
            updated_file_content = file_result[0]
            updated_row = file_result[1]
            # Загружаем обновленный файл на Яндекс.Диск
            if not updated_file_content:
                raise ValueError("Ошибка при обновлении Excel-файла.")

            async with aiohttp.ClientSession() as session:
                async with session.put(upload_url, data=updated_file_content) as upload_response:
                    if upload_response.status == 201:
                        result = updated_row
                        self.logger.info(message="Файл успешно обновлен на Яндекс.Диске.")
                    else:
                        raise RuntimeError(f"Ошибка при загрузке файла: {upload_response.status}")
        except Exception as e:
            result = None
            self.logger.error(message=f"Произошла ошибка при обновлении файла на Яндекс.Диске: {e}")
        finally:
            self.delete_temp_file()
        return result

    async def download_file(self):
        """Скачивает файл по URL и сохраняет его во временном месте."""
        download_url = await self.get_download_link()
        if not download_url:
            self.logger.error(message="Ошибка: Не удалось получить ссылку для скачивания файла.")
            return

        async with aiohttp.ClientSession() as session:
            async with session.get(download_url) as response:
                if response.status == 200:
                    file_content = await response.read()
                    with open(self.local_file_path, "wb") as f:
                        f.write(file_content)
                    return self.local_file_path
                else:
                    self.logger.error(message="Ошибка скачивания файла с Яндекс.Диск")
                    return None

    async def get_download_link(self):
        """Получает ссылку для скачивания файла."""
        url = f"{self.api_base}/resources/download?path={Config.YANDEX_DISK_FILE_PATH}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    json_response = await response.json()
                    return json_response.get("href")
                else:
                    self.logger.error(message=f"Ошибка при получении ссылки для скачивания: {response.status}")
                    return None

    async def get_upload_link(self):
        """Получает ссылку для загрузки файла."""
        url = f"{self.api_base}/resources/upload?path={Config.YANDEX_DISK_FILE_PATH}&overwrite=true"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    json_response = await response.json()
                    return json_response.get("href")
                else:
                    self.logger.error(message=f"Ошибка при получении ссылки для загрузки: {response.status}")
                    return None


    async def update_excel_file(self, file_path: str,
                          sheet_name: Optional[str] = None,
                          needle_column: Optional[str] = None,
                          needle_value: Optional[str] = None,
                          **kwargs
                          ):
        """Обновляет Excel-файл, добавляя новые данные."""
        try:
            # 1. Читаем Excel-файл
            excel_data = pd.read_excel(file_path, sheet_name=None, dtype=str)

            # Проверяем, существует ли указанный лист
            if sheet_name and sheet_name not in excel_data:
                raise ValueError(f"Лист '{sheet_name}' не найден в файле.")

            # Выбираем нужный лист для обновления
            sheet = excel_data[sheet_name if sheet_name else 0]

            # Проверяем, существует ли нужная колонка
            if needle_column and needle_column not in sheet.columns:
                raise ValueError(f"Колонка '{needle_column}' не найдена в файле.")

            # 2. Находим строку для обновления
            if needle_value and needle_column:
                # Приводим needle_value к строке и удаляем пробелы
                needle_value_str = str(needle_value).strip()

                # Приводим все значения в столбце к строкам и удаляем пробелы
                sheet[needle_column] = sheet[needle_column].astype(str).str.strip()

                # Ищем индекс строки, где значение в столбце совпадает с needle_value
                target_row_index = sheet[sheet[needle_column] == needle_value_str].index

                if target_row_index.empty:
                    raise RuntimeError(f"Строка с {needle_column}={needle_value} не найдена в файле.")
                target_row_index = target_row_index[0]
            elif needle_column and not needle_value:
                if needle_column not in sheet.columns:
                    raise ValueError(f"Колонка '{needle_column}' не найдена в файле.")
                target_row_index = sheet[sheet[needle_column].isnull()].index  # Ищем пустые значения в колонке needle_column
                if target_row_index.empty:
                    raise ValueError(f"Пустые строки в колонке '{needle_column}' не найдены.")
                target_row_index = target_row_index[0]
            else:
                # Если needle_column и needle_value не указаны:
                # Ищем первую пустую строку в первом столбце
                target_row_index = sheet[sheet.iloc[:, 0].isnull()].index

                if target_row_index.empty:
                    # Если пустых строк нет, добавляем новую строку в конец таблицы
                    new_row = {col: None for col in sheet.columns}  # Создаем новую строку с None для всех столбцов
                    # Используем pd.concat вместо .append()
                    sheet = pd.concat([sheet, pd.DataFrame([new_row])], ignore_index=True)
                    target_row_index = len(sheet) - 1  # Индекс новой строки будет последним
                else:
                    # Если пустая строка найдена, используем её индекс
                    target_row_index = target_row_index[0]


            # 4. Обновляем данные в найденной строке (динамически)
            for column, value in kwargs.items():
                if column in sheet.columns:
                    sheet.loc[target_row_index, column] = value

            # 5. Сохраняем обновленный DataFrame обратно в Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Записываем обновленный лист
                excel_data[sheet_name if sheet_name else 0] = sheet

                # Записываем все листы в файл
                for name, data in excel_data.items():
                    # Приводим название листа к строке
                    sht_name = str(name)[:31]  # Ограничиваем длину имени листа до 31 символа (ограничение Excel)
                    data.to_excel(writer, sheet_name=sht_name, index=False)
            output.seek(0)
            self.logger.info(message=f"Добавлена новая строка в файл.")
            return [output.getvalue(), sheet.loc[target_row_index]]
        except Exception as e:
            self.logger.error(message=f"Ошибка при обновлении Excel-файла: {e}")
            return None

    def validate_data(self, data):

        """Валидирует входные данные."""
        required_fields = []  # Укажите необходимые поля, если они есть
        if not all(field in data for field in required_fields):
            self.logger.error(message=f"Отсутствуют обязательные поля в данных: {data}")
            return False
        return True

    def delete_temp_file(self):
        """Удаляет временный файл после использования."""
        if os.path.exists(self.local_file_path):
            os.remove(self.local_file_path)
