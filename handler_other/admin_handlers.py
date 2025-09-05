# from aiogram import types, Router, F
# from aiogram.filters import Command
# from aiogram.fsm.context import FSMContext

# from bot.utils.keyboards import Keyboards
# from bot.utils.messages import Messages

# from bot.database.repositories.user_repository import *
# from bot.database.models import Report

# from bot.utils.state import RequestForm

# #from bot.handlers.start_handlers import start_command

# import logging

# router = Router()

# def register_handlers(dp: Router):
#     #logging.info(f"Регистрируем роутер {router} в диспетчере {dp}")
#     dp.include_router(router)


# @router.message(Command('reg_admin_2901'))
# async def reg_admin(message: types.Message):
#     admin_id = message.from_user.id
#     async with AdminRepository() as admin_db:
#         await admin_db.sign_up(admin_id)
#     await message.answer(text='Вы успешно зарегестрировались в качестве администратора, чтобы войти введите /admin', reply_markup=Keyboards.admin_exit())


# @router.message(Command('admin'))
# async def sign_up_admin(message: types.Message, state: FSMContext):
#     admin_id = message.from_user.id
#     async with AdminRepository() as admin_db:
#         result = await admin_db.get_admin(admin_id)
#     if result is None:
#         await message.answer(text='Вы не администратор')
#         await start_command(message)
#     else:
#         await state.set_state(RequestForm.admin)
#         async with ReportRepository() as report_db:
#             report: list[Report] = await report_db.get_admin_report()
#         if len(report) != 0:
#             await message.answer(text='Доступные заявки', reply_markup=Keyboards.admin_exit())
#             for index, item in enumerate(report):
#                 item = item.to_dict()
#                 text, photo = Messages.format_report_message(item)
#                 if len(photo) != 0:
#                     await message.answer_photo(photo=photo[0], caption=text, reply_markup=Keyboards.admin_inline(item.get('id')))
#                 else:
#                     await message.answer(text=text, reply_markup=Keyboards.admin_inline(item.get('id')))
                
#         else:
#             await message.answer(text='Нет доступных заявок', reply_markup=Keyboards.admin_exit())
            
# @router.message(F.text == 'Выйти')
# async def exit_from_admin(message: types.Message, state: FSMContext):
#     await state.clear()
#     await start_command(message)


# @router.message(F.text == 'Добавить ФФ исполнителя')
# async def add_ff(message: types.Message, state: FSMContext):
#     await message.answer(text='Введите @username')
#     await state.set_state(RequestForm.wait_ff)

# @router.message(RequestForm.wait_ff)
# async def add_executer(message: types.Message, state: FSMContext):
#     username = message.text
#     async with FFExecuterRepository() as ff_db:
#         await ff_db.add_ff_executer(username)
#     await message.answer(text='ФФ зарегестрирован', reply_markup=Keyboards.admin_exit())
#     await state.set_state(RequestForm.admin)






