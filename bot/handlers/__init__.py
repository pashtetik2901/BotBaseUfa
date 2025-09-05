import importlib
import os

from aiogram import Router

def setup_handlers(dp: Router):
    handlers_dir = os.path.dirname(__file__)
    for file in os.listdir(handlers_dir):
        if file.endswith("_handler.py") or file.endswith("_handlers.py"):
            module_name = file[:-3]  # Убираем ".py"
            try:
                module = importlib.import_module(f"bot.handlers.{module_name}")
                if hasattr(module, "register_handlers"):
                    module.register_handlers(dp)
            except Exception as e:
                print(f"[ERROR] Не удалось загрузить {module_name}: {e}")
                