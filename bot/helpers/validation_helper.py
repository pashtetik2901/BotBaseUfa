import datetime
import re


class ValidationHelper:
    @staticmethod
    def validate_car_number(car_number: str) -> bool:
        # Пример валидации регистрационного номера (может потребоваться доработка)
        return re.match(r"^[АВЕКМНОРСТУХ]\d{3}[АВЕКМНОРСТУХ]{2}\d{2,3}$", car_number, re.IGNORECASE) is not None

    @staticmethod
    def validate_card_number(card_number: str) -> bool:
        """
        Проверяет, является ли строка корректным номером банковской карты.
        Формат: от 13 до 19 цифр.
        """
        return re.match(r"^\d{13,19}$", card_number) is not None

    @staticmethod
    def validate_phone(phone: str) -> bool:
        cleaned_phone = re.sub(r"[^\d+]", "", phone)
        return re.match(r"^\+[78]\d{10}$", cleaned_phone) is not None

    @staticmethod
    def validate_date_time(date_time: str) -> bool:
        """
        Проверяет, является ли строка корректной датой и временем.
        Формат: дд.мм.гггг чч:мм
        """
        try:
            datetime.datetime.strptime(date_time, "%d.%m.%Y %H:%M")
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_only_numbers(value: str) -> bool:
        """
        Проверяет, состоит ли строка только из цифр.
        """
        return value.isdigit()

    @staticmethod
    def validate_float_or_int(value: str) -> bool:
        """
        Проверяет, является ли строка корректным числом (float или int).
        Формат: необязательный минус (-), цифры, необязательная точка и цифры.
        Примеры допустимых значений: "123", "123.45", "-0.12", "0".
        """
        return re.match(r"^-?\d+(\.\d+)?$", value) is not None

    @staticmethod
    def validate_time(value: str) -> bool:
        """
        Проверяет, является ли строка временем
        """
        return re.match(r"^\d{1,2}:\d{2}$", value) is not None
