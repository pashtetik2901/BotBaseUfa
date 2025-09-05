class Messages:
    ERROR_CREATE_USER = "Ошибка создания пользователя"
    ERROR_USER_NOT_FOUND = "Пользователь не найден."
    ERROR_WRONG_PHONE_NUMBER = "Неверный формат номера телефона. Попробуйте снова."
    ERROR_WRONG_DATA = "Неверные данные"

    BUTTON_AUTHORIZE = "Авторизоваться"
    BUTTON_SELECT = "Выбрать"
    BUTTON_OK = "ОК"
    BUTTON_CANCEL = "Отмена"

    WELCOME_MESSAGE = 'Hello Bot'

    @staticmethod
    def format_report_message(report: dict) -> tuple[str, list]:

        location = report.get("location", "Не указано")
        storage = report.get("storage", "Не указано")
        category = report.get("category", "Не указано")
        size = report.get("size", "Не указано")
        count = report.get("count", "Не указано")
        attachments = report.get("attachments")
        pack = report.get("pack", "Не указано")
        comment = report.get("comment", "Нет")
        seller_username = report.get("seller_username", "Не указан")

        # Проверяем, есть ли вложения и не пустой ли список
        has_attachments = bool(attachments and isinstance(attachments, list) and len(attachments) > 0)

        if not has_attachments:
            # Вариант без вложений — обычный текст
            message = (
                "Новый Заказ на упаковку и отгрузку:\n\n"
                f"1. Место нахождения товара:\n{location}\n\n"
                f"2. Склад отгрузки:\n{storage}\n\n"
                f"3. Категория товара:\n{category}\n\n"
                f"4. Габариты товара:\n{size}\n\n"
                f"5. Количество товаров:\n{count}\n\n"
                f"6. Вложения:\nНет вложений\n\n"
                f"7. Желаемый вид упаковки:\n{pack}\n\n"
                f"8. Комментарий от заказчика:\n{comment}\n\n"
                f"9. Контакт для связи:\n@{seller_username}"
            )
            photos = []
        else:
            # Вариант с вложениями — текст с указанием, что фото есть
            message = (
                "Новый Заказ на упаковку и отгрузку (с фото):\n\n"
                f"1. Место нахождения товара:\n{location}\n\n"
                f"2. Склад отгрузки:\n{storage}\n\n"
                f"3. Категория товара:\n{category}\n\n"
                f"4. Габариты товара:\n{size}\n\n"
                f"5. Количество товаров:\n{count}\n\n"
                f"6. Вложения: фото во вложении\n\n"
                f"7. Желаемый вид упаковки:\n{pack}\n\n"
                f"8. Комментарий от заказчика:\n{comment}\n\n"
                f"9. Контакт для связи:\n@{seller_username}"
            )
            # Предполагаем, что attachments — список URL или путей к фото
            photos = attachments  # или преобразуйте в нужный формат для отправки

        return message, photos

    def format_report_message_for_channel(report: dict) -> tuple[str, list]:

        location = report.get("location", "Не указано")
        storage = report.get("storage", "Не указано")
        category = report.get("category", "Не указано")
        size = report.get("size", "Не указано")
        count = report.get("count", "Не указано")
        attachments = report.get("attachments")
        pack = report.get("pack", "Не указано")
        comment = report.get("comment", "Нет")
        seller_username = report.get("seller_username", "Не указан")

        # Проверяем, есть ли вложения и не пустой ли список
        has_attachments = bool(attachments and isinstance(attachments, list) and len(attachments) > 0)

        if not has_attachments:
            # Вариант без вложений — обычный текст
            message = (
                "Новый Заказ на упаковку и отгрузку:\n\n"
                f"1. Место нахождения товара:\n{location}\n\n"
                f"2. Склад отгрузки:\n{storage}\n\n"
                f"3. Категория товара:\n{category}\n\n"
                f"4. Габариты товара:\n{size}\n\n"
                f"5. Количество товаров:\n{count}\n\n"
                f"6. Вложения:\nНет вложений\n\n"
                f"7. Желаемый вид упаковки:\n{pack}\n\n"
                f"8. Комментарий от заказчика\n{comment}\n\n"
            )
            photos = []
        else:
            # Вариант с вложениями — текст с указанием, что фото есть
            message = (
                "Новый Заказ на упаковку и отгрузку (с фото):\n\n"
                f"1. Место нахождения товара:\n{location}\n\n"
                f"2. Склад отгрузки:\n{storage}\n\n"
                f"3. Категория товара:\n{category}\n\n"
                f"4. Габариты товара:\n{size}\n\n"
                f"5. Количество товаров:\n{count}\n\n"
                f"6. Вложения: фото во вложении\n\n"
                f"7. Желаемый вид упаковки:\n{pack}\n\n"
                f"8. Комментарий от заказчика:\n{comment}\n\n"
            )
            # Предполагаем, что attachments — список URL или путей к фото
            photos = attachments  # или преобразуйте в нужный формат для отправки

        return message, photos

