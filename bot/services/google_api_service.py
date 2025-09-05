import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from bot.config import BASE_DIR, Config
from bot.helpers.file_logger import CustomLogger


class GoogleSheetsService:
    def __init__(self, spreadsheet_id: str):
        # Настройка доступа к Google Sheets
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(Config.GOOGLE_CREDENTIALS_FILE, scope)
        gc = gspread.authorize(credentials)

        """Инициализация сервиса Google Sheets"""
        self.sheet = gc.open_by_key(spreadsheet_id)
        self.logger = CustomLogger('googlesheet', log_to_console=False, log_to_file=True)

    def get_sheet(self, sheet_name: str) -> gspread.Worksheet:
        """Получает лист по имени"""
        try:
            return self.sheet.worksheet(sheet_name)
        except Exception as e:
            self.logger.error( message=f"Ошибка при получении листа {sheet_name}: {e}")
            raise

    def check_and_create_sheet(self, sheet_name: str, headers: list) -> bool:
        """Проверяет существование листа и создает его при необходимости"""
        try:
            sheet = self.get_sheet(sheet_name)
            self.logger.info(message=f"Лист {sheet_name} существует.")
            return True
        except gspread.exceptions.WorksheetNotFound:
            self.logger.info(message=f"Лист {sheet_name} не найден. Создаем новый...")
            sheet = self.sheet.add_worksheet(title=sheet_name, rows="100", cols="20")
            sheet.append_row(headers)
            self.logger.info(message=f"Лист {sheet_name} успешно создан.")
            return True
        except Exception as e:
            self.logger.error( message=f"Ошибка при проверке/создании листа {sheet_name}: {e}")
            return False

    def save_data(self, data: dict, sheet_name: str) -> bool:
        """Сохраняет данные в Google Sheets"""
        try:
            # Получаем нужный лист
            sheet = self.get_sheet(sheet_name)

            # Преобразуем данные в список для записи
            row = [str(data.get(key, '')) for key in sheet.row_values(1)]

            # Добавляем новую строку
            sheet.append_row(row)
            self.logger.info(message=f"Данные успешно сохранены в лист {sheet_name}: {data}")
            return True
        except Exception as e:
            self.logger.error( message=f"Ошибка при сохранении данных в лист {sheet_name}: {e}")
            return False

    def get_current_data(self, sheet_name: str) -> list:
        """Получает текущие данные из листа"""
        try:
            # Получаем нужный лист
            sheet = self.get_sheet(sheet_name)
            # Читаем все записи
            records = sheet.get_all_records()
            self.logger.info(message=f"Получено {len(records)} записей из листа {sheet_name}.")
            return records
        except Exception as e:
            self.logger.error( message=f"Ошибка при чтении данных из листа {sheet_name}: {e}")
            return []