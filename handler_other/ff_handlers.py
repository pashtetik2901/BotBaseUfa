from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from main import bot
from bot.config import Config

from bot.handlers.start_handlers import check

from bot.utils.keyboards import Keyboards
from bot.utils.messages import Messages

from bot.database.repositories.user_repository import *
from bot.database.models import Report
from bot.utils.state import RequestForm

router = Router()


def register_handlers(dp: Router):
    dp.include_router(router)


@router.message(F.text == 'ФФ')
async def ff_menu(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    chat_member = await bot.get_chat_member(chat_id=Config.LINK_CHANNEL, user_id=user_id)

    async with FFExecuterRepository() as ff_db:
        executer = await ff_db.get_executer(username)
    

    if  check(chat_member) and executer:
        await message.answer(text=f'Чтобы откликнуться на заявки посетите канал: {Config.LINK_CHANNEL}', reply_markup=Keyboards.ff_menu())
        await state.set_state(RequestForm.ff_executer)
    else:
        await message.answer(text=f'Чтобы стать исполнителем вам нужно подписать на канал {Config.LINK_CHANNEL}', reply_markup=Keyboards.chek_channel())
        #await state.set_state(RequestForm.wait_channel)

@router.message(F.text == 'Доступные заявки', RequestForm.ff_executer)
async def send_link_channel(message: types.Message):
    await message.answer(text=f'Вы можете откликнуться на заявки в канале {Config.LINK_CHANNEL}')

@router.message(F.text == 'Мои заявки', RequestForm.ff_executer)
async def my_report_ff(message: types.Message):
    ff_id = message.from_user.id
    async with ResponseRepository() as res_db:
        result: list[Response] = await res_db.get_all_my_response(ff_id)
    if len(result) != 0:
        await message.answer(text='Ваши отклики', reply_markup=Keyboards.ff_menu())
        async with ReportRepository() as report_db:
            for index, item in enumerate(result):
                report: Report = await report_db.get_one_report(item.report_id)
                if report:
                    data = report.to_dict()
                    text, photo = Messages.format_report_message_for_channel(data)
                    if len(photo) != 0:
                        await message.answer_photo(photo=photo[0], caption=text, reply_markup=Keyboards.status_response(item.status))
                    else:
                        await message.answer(text=text, reply_markup=Keyboards.status_response(item.status))

    else:
        await message.answer(text='У вас нет откликов', reply_markup=Keyboards.ff_menu())

