import datetime

import pytz


class DateAndTimeHelper:

    @staticmethod
    def format_datetime_utc3(dt: datetime) -> str:
        """
        Форматирует дату и время в UTC+3.
        """
        if not dt:
            return "-"

        if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
            # Если дата/время не содержит информации о часовом поясе, считаем её UTC
            dt = pytz.utc.localize(dt)

        # Устанавливаем часовой пояс UTC+3
        moscow_tz = pytz.timezone('Europe/Moscow')
        dt_utc3 = dt.astimezone(moscow_tz)

        # Форматируем дату и время в нужном формате
        return dt_utc3.strftime('%d.%m.%Y %H:%M')

    @staticmethod
    def format_datetime(dt: datetime) -> str:
        """
        Форматирует дату и время
        """
        # Форматируем дату и время в нужном формате
        return dt.strftime('%d.%m.%Y %H:%M')

    @staticmethod
    def format_datetime_en(dt: datetime) -> str:
        """
        Форматирует дату и время
        """
        # Форматируем дату и время в нужном формате
        return dt.strftime('%Y-%m-%dT%H:%M:%S')

    @staticmethod
    def format_date(dt: datetime) -> str:
        """
        Форматирует дату и время
        """
        # Форматируем дату и время в нужном формате
        return dt.strftime('%d.%m.%Y')

    @staticmethod
    def convert_to_utc(dt: datetime):
        if dt.tzinfo is None:
            return dt.replace(tzinfo=datetime.timezone.utc)
        return dt

    @staticmethod
    def get_current_utc_time():
        return datetime.datetime.now(datetime.timezone.utc)

    @staticmethod
    def get_current_moscow_time():
        # Текущее время в UTC
        current_time_utc = datetime.datetime.now(pytz.utc)

        # Преобразуем текущее время в московский часовой пояс (UTC+3)
        moscow_tz = pytz.timezone('Europe/Moscow')
        return current_time_utc.astimezone(moscow_tz)

    @staticmethod
    def convert_str_to_datetime(txt: str):
        try:
            dt = datetime.datetime.strptime(txt, "%d.%m.%Y %H:%M:%S")
        except:
            dt = None
        return dt

    @staticmethod
    def convert_str_to_date(txt: str):
        try:
            dt = datetime.datetime.strptime(txt, "%Y-%m-%d")
        except:
            dt = None
        return dt

    @staticmethod
    def convert_date_to_datetimetz(txt: str):
        txt_dt = datetime.datetime.strptime(txt, "%d.%m.%Y")  # Парсим строку в datetime
        txt_dt = txt_dt.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=3)))  # Устанавливаем часовой пояс +03:00
        formatted_txt = txt_dt.strftime("%Y-%m-%dT%H:%M:%S%z")
        formatted_txt = formatted_txt[:-2] + ":" + formatted_txt[-2:]
        return formatted_txt