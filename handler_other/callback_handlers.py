from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from main import bot
from bot.config import Config

from bot.utils.keyboards import Keyboards
from bot.utils.messages import Messages

from bot.database.repositories.user_repository import *
from bot.database.models import Report

from bot.handlers.start_handlers import check

router = Router()


def register_handlers(dp: Router):
    dp.include_router(router)


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
async def delete_report(callback: types.CallbackQuery):
    report_id = callback.data.removeprefix('delete_admin_')
    async with ReportRepository() as report_db:
        report: dict = await report_db.delete_report(report_id)
    if report:
        await bot.send_message(chat_id=report.get('seller_id'), text=f'Ваша заявка отклонена\n' + "\n".join(f"{k}: {v}" for k, v in report.items()))
        await callback.message.delete()
    else:
        await callback.answer(text='Произошла какая то ошибка')


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
        await callback.message.answer(text='Вы подписались! Далее обратитесь к администратору')
    else:
        await callback.message.answer(text='Вы не подписались')


@router.callback_query(F.data.startswith('answer_'))
async def answer_on_report(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    username = callback.from_user.username
    report_id = callback.data.removeprefix('answer_')

    async with FFExecuterRepository() as ff_db:
        executer = await ff_db.get_executer(username)
        if executer is None:
            await bot.send_message(chat_id=user_id, text='Вы не зарегестрированы в качетве исполнителя')
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