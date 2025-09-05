from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage



class RequestForm(StatesGroup):
    seller = State()
    ff_executer = State()
    admin = State()
    location = State()
    warehouse = State()
    category = State()
    size = State()
    quantity = State()
    attachments = State()
    packaging = State()
    comment = State()
    agree = State()
    wait_ff = State()
    wait_channel = State()
    wait_reason = State()

storage = MemoryStorage()

