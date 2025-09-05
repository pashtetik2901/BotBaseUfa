from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.utils.keyboards import Keyboards
from bot.utils.messages import Messages

from bot.database.repositories.user_repository import *
from bot.database.models import Report

from bot.utils.state import RequestForm
from bot.config import Config
from main import bot

import logging

router = Router()

def register_handlers(dp: Router):
    #logging.info(f"Регистрируем роутер {router} в диспетчере {dp}")
    dp.include_router(router)


# @router.message(Command('reg_admin_2901'))
# async def reg_admin(message: types.Message):
#     admin_id = message.from_user.id
#     async with AdminRepository() as admin_db:
#         await admin_db.sign_up(admin_id)
#     await message.answer(text='Вы успешно зарегестрировались в качестве администратора, чтобы войти введите /admin', reply_markup=Keyboards.admin_exit())


@router.message(Command('admin'))
async def sign_up_admin(message: types.Message, state: FSMContext):
    admin_id = message.from_user.id
    admin_username = f'@{message.from_user.username}'
    result: list[str] = Config.ADMIN_IDS

    # async with AdminRepository() as admin_db:
    #     result = await admin_db.get_admin(admin_id)
    # if result is None:

    if admin_username not in result:
        await message.answer(text='Вы не администратор')
        await start_command(message)
    else:
        await state.set_state(RequestForm.admin)
        async with ReportRepository() as report_db:
            report: list[Report] = await report_db.get_admin_report()
        if len(report) != 0:
            await message.answer(text='Доступные заявки', reply_markup=Keyboards.admin_exit())
            for index, item in enumerate(report):
                item = item.to_dict()
                text, photo = Messages.format_report_message(item)
                if len(photo) != 0:
                    await message.answer_photo(photo=photo[0], caption=text, reply_markup=Keyboards.admin_inline(item.get('id')))
                else:
                    await message.answer(text=text, reply_markup=Keyboards.admin_inline(item.get('id')))
                
        else:
            await message.answer(text='Нет доступных заявок', reply_markup=Keyboards.admin_exit())
            
@router.message(F.text == 'Выйти')
async def exit_from_admin(message: types.Message, state: FSMContext):
    await state.clear()
    await start_command(message)


@router.message(F.text == 'Добавить ФФ исполнителя')
async def add_ff(message: types.Message, state: FSMContext):
    await message.answer(text='Введите @username')
    await state.set_state(RequestForm.wait_ff)

@router.message(RequestForm.wait_ff)
async def add_executer(message: types.Message, state: FSMContext):
    username = message.text
    async with FFExecuterRepository() as ff_db:
        await ff_db.add_ff_executer(username)
    await message.answer(text='ФФ зарегестрирован', reply_markup=Keyboards.admin_exit())
    await state.set_state(RequestForm.admin)






@router.callback_query(F.data.startswith('publish_'))
async def publish_report(callback: types.CallbackQuery):
    report_id = callback.data.removeprefix('publish_')
    async with ReportRepository() as report_db:
        report: dict = await report_db.update_status(report_id, 'Опубликован')
    if report:
        text, photo = Messages.format_report_message_for_channel(report)
        if len(photo) != 0:
            message = await bot.send_photo(chat_id=Config.LINK_CHANNEL, photo=photo[0], caption=text, reply_markup=Keyboards.answer_inline(report.get('id')))
            message_id = message.message_id
        else:
            message = await bot.send_message(chat_id=Config.LINK_CHANNEL, text=text, reply_markup=Keyboards.answer_inline(report.get('id')))
            message_id = message.message_id
        async with report_db:
            await report_db.update_message_id(report_id, message_id)
        await callback.message.delete()



@router.callback_query(F.data.startswith('delete_admin_'))
async def delete_report(callback: types.CallbackQuery, state: FSMContext):
    report_id = callback.data.removeprefix('delete_admin_')
    await state.update_data(report_id = report_id)
    await callback.message.answer(text='Введите причину отклонения заявки')
    await state.set_state(RequestForm.wait_reason)


@router.message(F.text, RequestForm.wait_reason)
async def reason_cancel(message: types.Message, state: FSMContext):
    data = await state.get_data()
    reason = message.text
    report_id = data.get('report_id')

    async with ReportRepository() as report_db:
        report: dict = await report_db.delete_report(report_id)
    
    if report:
        seller_id = report.get('seller_id')
        await bot.send_message(chat_id=seller_id, text='Ваша заявка отклонена')

        text, photo = Messages.format_report_message(report)
        if len(photo) != 0:
            await bot.send_photo(chat_id=seller_id, photo=photo[0], caption=text)
        else:
            await bot.send_message(chat_id=seller_id, text=text)

        await bot.send_message(chat_id=seller_id, text=f'Причина отклонения заявки: {reason}')
        await state.set_state(RequestForm.admin)
    else:
        await message.answer(text='Произошла ошибка')
    


@router.callback_query(F.data.startswith('delete_seller_'))
async def delete_seller(callback: types.CallbackQuery):
    await callback.answer()
    report_id = callback.data.removeprefix('delete_seller_')
    async with ReportRepository() as report_db:
        report = await report_db.delete_report(report_id)
    await callback.message.delete()
    if report.get('message_id'):
        await bot.delete_message(chat_id=Config.LINK_CHANNEL, message_id=report.get('message_id'))


@router.callback_query(F.data.startswith('chek_pod'))
async def check_podpiska(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    chat_member = await bot.get_chat_member(chat_id=Config.LINK_CHANNEL, user_id=user_id)
    if check(chat_member):
        await callback.message.answer(text=f'Вы подписались! Оставить отклик можете здесь: {Config.SHARE_LINK}')
    else:
        await callback.message.answer(text='Вы не подписаны на канал')


@router.callback_query(F.data.startswith('answer_'))
async def answer_on_report(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    username = callback.from_user.username
    report_id = callback.data.removeprefix('answer_')

    async with FFExecuterRepository() as ff_db:
        executer = await ff_db.get_executer(username)
        if executer is None:
            await bot.send_message(chat_id=user_id, text=f'Вы не зарегестрированы в качетве исполнителя, обратитесь к администратору - {Config.ADMIN_IDS[0]}')
        else:
            async with ReportRepository() as report_db:
                report: Report = await report_db.get_one_report(report_id)
            if report:
                data = report.to_dict()
                text, photo = Messages.format_report_message_for_channel(data)
                if len(photo) != 0:
                    await bot.send_photo(chat_id=user_id, photo=photo[0], caption=text, reply_markup=Keyboards.inline_answer(data.get('id')))
                else:
                    await bot.send_message(chat_id=user_id, text=text, reply_markup=Keyboards.inline_answer(data.get('id')))



@router.callback_query(F.data.startswith('agree_answer_'))
async def agree_with_answer_ff(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    username = callback.from_user.username
    report_id = callback.data.removeprefix('agree_answer_')
    async with ReportRepository() as report_db:
        report: Report = await report_db.get_one_report(report_id)
    if report:
        seller_id = report.seller_id
        async with ResponseRepository() as res_db:
            response_id = await res_db.add_response(report_id, seller_id, user_id)
        await callback.message.answer(text=f'Вы откликнулись на заявку, можете связаться с селлером - @{report.seller_username}')
        await bot.send_message(chat_id=report.seller_id, text=f'На вашу заявку откликнулись - @{username}', reply_markup=Keyboards.inline_agree_seller(response_id))


@router.callback_query(F.data.startswith('disagree_answer_'))
async def disagree_with_answer(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()


@router.callback_query(F.data.startswith('agree_seller_'))
async def agree_seller_with_answer(callback: types.CallbackQuery, state: FSMContext):
    response_id = callback.data.removeprefix('agree_seller_')
    response_id = int(response_id)
    async with ResponseRepository() as res_db:
        response = await res_db.update_status(response_id, 'Принято')
        async with ReportRepository() as report_db:
            report = await report_db.update_status(response.report_id, 'В работе')
        await bot.send_message(chat_id=response.ff_id, text=f'Ваш отклик приняли в работу')
        result: list[Response] = await res_db.disagree_response(response_id)
        if result:
            for item in result:
                await res_db.update_status(item.id, 'Отклонено')
                await bot.send_message(chat_id=item.ff_id, text='Селлер выбрал другого исполнителя')



@router.callback_query(F.data.startswith('complete_seller_'))
async def complete_report(callback: types.CallbackQuery, state: FSMContext):
    report_id = callback.data.removeprefix('complete_seller_')
    async with ReportRepository() as report_db:
        report = await report_db.update_status(report_id, 'Выполнено')
        if report:
            await bot.delete_message(chat_id=Config.LINK_CHANNEL, message_id=report.get('message_id'))
            async with ResponseRepository() as res_db:
                response = await res_db.update_status_pro(report.get('id'), report.get('seller_id'), 'Выполнено')
                await bot.send_message(chat_id=response.ff_id, text='Вы выполнили заявку')


@router.message(F.text == 'ФФ')
async def ff_menu(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    chat_member = await bot.get_chat_member(chat_id=Config.LINK_CHANNEL, user_id=user_id)

    async with FFExecuterRepository() as ff_db:
        executer = await ff_db.get_executer(username)
    

    if  check(chat_member) and executer:
        await message.answer(text=f'Чтобы откликнуться на заявки посетите канал: {Config.SHARE_LINK}', reply_markup=Keyboards.ff_menu())
        await state.set_state(RequestForm.ff_executer)
    else:
        await message.answer(text=f'Чтобы стать ФФ исполнителем обратитесь к администратору - {Config.ADMIN_IDS[0]}\n и подпишитесь на канал - {Config.SHARE_LINK}', reply_markup=Keyboards.chek_channel())
        #await state.set_state(RequestForm.wait_channel)

@router.message(F.text == 'Доступные заявки', RequestForm.ff_executer)
async def send_link_channel(message: types.Message):
    await message.answer(text=f'Вы можете откликнуться на заявки в канале {Config.SHARE_LINK}')

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

@router.message(Command('start'))
async def start_command(message: types.Message):
    await message.answer(text='Выберите роль', reply_markup=Keyboards.choose_role())


@router.message(F.text == 'Селлер')
async def seller_menu_tg(message: types.Message, state: FSMContext):
    await state.set_state(RequestForm.seller)
    await message.answer('Главное меню', reply_markup=Keyboards.seller_menu())


@router.message(F.text == "Подать заявку", RequestForm.seller)
async def start_request(message: types.Message, state: FSMContext):
    await state.update_data(seller_id=message.from_user.id)
    await state.update_data(seller_username=message.from_user.username)
    await state.set_state(RequestForm.location)
    await message.answer("Введите место нахождения товара:")


@router.message(RequestForm.location)
async def process_location(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    await state.set_state(RequestForm.warehouse)
    await message.answer("Введите склад отгрузки:")


@router.message(RequestForm.warehouse)
async def process_warehouse(message: types.Message, state: FSMContext):
    await state.update_data(storage=message.text)
    await state.set_state(RequestForm.category)
    await message.answer("Введите категорию товара:")


@router.message(RequestForm.category)
async def process_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await state.set_state(RequestForm.size)
    await message.answer("Введите габариты товара:")


@router.message(RequestForm.size)
async def process_size(message: types.Message, state: FSMContext):
    await state.update_data(size=message.text)
    await state.set_state(RequestForm.quantity)
    await message.answer("Введите количество товаров:")


@router.message(RequestForm.quantity)
async def process_quantity(message: types.Message, state: FSMContext):
    try:
        await state.update_data(count=int(message.text))
        await state.set_state(RequestForm.attachments)
        await message.answer("Прикрепите вложения (фото, документы) или нажмите 'Пропустить':", reply_markup=Keyboards.cancel_reply_button())
    except:
        await message.answer(text='Вы неправильно указали количество, введите снова')


@router.message(RequestForm.attachments, F.content_type.in_({"photo", "document"}))
async def process_attachments(message: types.Message, state: FSMContext):
    # Сохраняем file_id вложения
    data = await state.get_data()
    attachments = data.get("attachments", [])
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document:
        file_id = message.document.file_id
    else:
        file_id = None
    if file_id:
        attachments.append(file_id)
        await state.update_data(attachments=attachments)
    await message.answer("Вложение сохранено. Можно отправить ещё или нажать 'Пропустить'.", reply_markup=Keyboards.cancel_reply_button())


@router.message(RequestForm.attachments, F.text.casefold() == "пропустить")
async def skip_attachments(message: types.Message, state: FSMContext):
    await state.set_state(RequestForm.packaging)
    await message.answer("Введите желаемый вид упаковки:")


@router.message(RequestForm.packaging)
async def process_packaging(message: types.Message, state: FSMContext):
    await state.update_data(pack=message.text)
    await state.set_state(RequestForm.comment)
    await message.answer("Введите комментарий к заявке:")


@router.message(RequestForm.comment)
async def process_comment(message: types.Message, state: FSMContext):
    await state.update_data(comment=message.text)
    data = await state.get_data()
    text, photo = Messages.format_report_message(data)
    if len(photo) != 0:
        await message.answer_photo(photo=photo[0], caption=text, reply_markup=Keyboards.agree_keyboard())
    else:
        await message.answer(text=text, reply_markup=Keyboards.agree_keyboard())

    await state.set_state(RequestForm.agree)


@router.message(RequestForm.agree)
async def publish_report(message: types.Message, state: FSMContext):
    if message.text == 'Опубликовать':
        await state.update_data(status='Модерация')
        data = await state.get_data()
        async with ReportRepository() as report_db:
            await report_db.add_report(data)
        await message.answer(text='Отправлено на модерацию', reply_markup=Keyboards.seller_menu())

        for id in Config.ADMIN_ID_NUMBER:
            await bot.send_message(chat_id=id, text='У вас новая заявка на модерации, перейдите в админ панель')

        await state.set_state(RequestForm.seller)
        # await seller_menu_tg(message, state)
    elif message.text == 'Отменить':
        # await state.set_state(RequestForm.seller)
        # await seller_menu_tg(message, state)
        await message.answer(text='Вы уверены?', reply_markup=Keyboards.inline_agree_disagree())

@router.callback_query(F.data.startswith('yes_cancel'))
async def yes_cancel(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(RequestForm.seller)
    await callback.message.answer(text='Вы отменили заявку', reply_markup=Keyboards.seller_menu())
    
@router.callback_query(F.data.startswith('no_cancel'))
async def no_cancel(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(text='Опубликуйте заявку', reply_markup=Keyboards.agree_keyboard())


@router.message(F.text == 'Мои заявки', RequestForm.seller)
async def my_report(message: types.Message):
    seller_id = message.from_user.id
    async with ReportRepository() as report_db:
        result: list[Report] = await report_db.get_my_report(seller_id)
    if len(result) != 0:
        await message.answer(text='Ваши заявки', reply_markup=Keyboards.seller_menu())
        for index, item in enumerate(result):
            item = item.to_dict()
            text, photo = Messages.format_report_message(item)
            if len(photo) != 0:
                await message.answer_photo(photo=photo[0], caption=text, reply_markup=Keyboards.inline_report(item.get('status'), item.get('id')))
            else:
                await message.answer(text=text, reply_markup=Keyboards.inline_report(item.get('status'), item.get('id')))

    else:
        await message.answer(text='У вас нет заявок', reply_markup=Keyboards.seller_menu())

def check(chat_member: types.ChatMember) -> bool:
    return chat_member.status not in ['left', 'kicked']

@router.message(Command('start'))
async def start_command(message: types.Message):
    await message.answer(text='Выберите роль', reply_markup=Keyboards.choose_role())

