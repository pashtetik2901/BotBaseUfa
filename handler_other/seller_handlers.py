from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.utils.keyboards import Keyboards
from bot.utils.messages import Messages

from bot.database.repositories.user_repository import *
from bot.database.models import Report
from bot.utils.state import RequestForm

router = Router()


def register_handlers(dp: Router):
    dp.include_router(router)


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
    await message.answer("Введите размеры товара:")


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
        await message.answer("Прикрепите вложения (фото, документы) или отправьте 'Пропустить':")
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
    await message.answer("Вложение сохранено. Можно отправить ещё или написать 'Пропустить'.")


@router.message(RequestForm.attachments, F.text.casefold() == "пропустить")
async def skip_attachments(message: types.Message, state: FSMContext):
    await state.set_state(RequestForm.packaging)
    await message.answer("Введите ожидаемый вид упаковки:")


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
        await state.set_state(RequestForm.seller)
        await seller_menu_tg(message, state)
    elif message.text == 'Отменить':
        await state.set_state(RequestForm.seller)
        await seller_menu_tg(message, state)


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
