from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from bot.config import Config

class Keyboards:

    @staticmethod
    def example_keyboard():
        return ReplyKeyboardMarkup(keyboard=[
            [
                KeyboardButton(text='Текст 1'),
                KeyboardButton(text='Текст 2'),

            ]
        ], resize_keyboard=True, one_time_keyboard=False, )
    
    @staticmethod
    def choose_role():
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text='ФФ')],
            [KeyboardButton(text='Селлер')],
            
        ], resize_keyboard=True, one_time_keyboard=False)
    
    @staticmethod
    def seller_keyboard():
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text='Подать заявку')],
            [KeyboardButton(text='Мои заявки')],
            [KeyboardButton(text='None')]
        ], resize_keyboard=True, one_time_keyboard=False)
    
    @staticmethod
    def seller_menu():
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text='Подать заявку')],
            [KeyboardButton(text='Мои заявки')],
            [KeyboardButton(text='Выйти')]
        ], resize_keyboard=True, one_time_keyboard=False)
    
    @staticmethod
    def ff_menu():
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text='Доступные заявки')],
            [KeyboardButton(text='Мои заявки')],
            [KeyboardButton(text='Выйти')]
        ],resize_keyboard=True)
    
    @staticmethod
    def agree_keyboard():
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text='Опубликовать')],
            [KeyboardButton(text='Отменить')]
        ], resize_keyboard=True, one_time_keyboard=True)
    
    @staticmethod
    def inline_report(status: str, id: int):
        button1 = InlineKeyboardButton(text='Отменить', callback_data=f'delete_seller_{id}')
        button2 = InlineKeyboardButton(text='В работе', callback_data='none')
        button3 = InlineKeyboardButton(text='Выполнено', callback_data=f'complete_seller_{id}')

        if status not in ['В работе']:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [button1],
                [button3]
            ])
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [button2],
                [button1],
                [button3]
            ])

        return keyboard
    
    @staticmethod
    def admin_inline(index: int):
        button1 = InlineKeyboardButton(text='Опубликовать', callback_data=f'publish_{index}')
        button2 = InlineKeyboardButton(text='Отклонить', callback_data=f'delete_admin_{index}')
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [button1],
            [button2]
        ])
        return keyboard
    
    @staticmethod
    def admin_exit():
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text='Выйти')],
            [KeyboardButton(text='Добавить ФФ исполнителя')]
        ], resize_keyboard=True)
    
    @staticmethod
    def answer_inline(index: int):
        button = InlineKeyboardButton(text='Откликнуться', callback_data=f'answer_{index}')
        return InlineKeyboardMarkup(inline_keyboard=[
            [button]
        ])
    
    @staticmethod
    def chek_channel():
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Проверить подписку', callback_data='chek_pod')]
        ])
    
    @staticmethod
    def inline_answer(index: int):
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Принять', callback_data=f'agree_answer_{index}')],
            [InlineKeyboardButton(text='Отклонить', callback_data=f'disagree_answer_{index}')]
        ])
    
    @staticmethod
    def inline_agree_seller(response_id: int):
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Принять', callback_data=f'agree_seller_{response_id}')]
        ])
    

    @staticmethod
    def status_response(status: str):
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=status, callback_data='none')]
        ])
    
    @staticmethod
    def inline_agree_disagree():
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Да', callback_data='yes_cancel')],
            [InlineKeyboardButton(text='Нет', callback_data='no_cancel')]    
        ])
    
    @staticmethod
    def cancel_reply_button():
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text='Пропустить')]
        ], resize_keyboard=True, one_time_keyboard=True)