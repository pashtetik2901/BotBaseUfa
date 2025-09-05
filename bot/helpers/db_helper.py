from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import Query
import sqlalchemy as sa

class DatabaseHelper:

    @staticmethod
    async def debug_query(query: Query):
        # Получаем SQL-запрос
        compiled_query = query.statement.compile(dialect=sa.dialects.sqlite.dialect(), compile_kwargs={"literal_binds": True})
        print(compiled_query)

    @staticmethod
    async def debug_select(query):
        """
        Выводит скомпилированный SQL-запрос для отладки.
        """
        # Компилируем запрос с подстановкой параметров
        compiled_query = query.compile(
            dialect=sqlite.dialect(),  # Используем диалект SQLite
            compile_kwargs={"literal_binds": True}  # Подставляем значения параметров
        )
        print(str(compiled_query))  # Выводим SQL-запрос