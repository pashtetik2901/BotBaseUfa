from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session, async_sessionmaker
from bot.database.db import engine
from bot.helpers.file_logger import CustomLogger


class BaseRepository:
    table: object = None

    def __init__(self, model, session=None):
        self.model = model
        self._provided_session = session  # Внешняя сессия, если передана
        self._local_session = None  # Сессия, созданная самим репозиторием
        self.logger = CustomLogger(source="db", log_to_file=True, log_to_console=False)
        # Инициализируем фабрику сессий только если не передана внешняя сессия
        if not session:
            self._session_factory = async_scoped_session(
                async_sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=engine,
                    class_=AsyncSession
                ),
                scopefunc=lambda: id(self)
            )

    def destroy(self):
        if self.logger is not  None:
            self.logger.destroy()
            self.logger = None

    @property
    def session(self) -> AsyncSession:
        """Главный геттер для получения текущей сессии"""
        if not hasattr(self, '_active_session'):
            if self._provided_session:
                self._active_session = self._provided_session
            else:
                raise RuntimeError("Session not initialized. Use context manager")
        return self._active_session

    async def __aenter__(self):
        """Инициализация сессии при входе в контекст"""
        if not self._provided_session:
            self._local_session = self._session_factory()
            self._active_session = self._local_session
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие сессии при выходе из контекста"""
        if self._local_session:
            await self._local_session.close()
            self._local_session = None
            self._active_session = None
        self.destroy()

    async def close_session(self):
        """Явное закрытие сессии"""
        if self._local_session:
            await self._local_session.close()
            self._local_session = None
            self._active_session = None

    async def commit(self):
        try:
            await self.session.commit()
        except Exception as e:
            await self.rollback()
            self.logger.error(message=f"Commit error: {e}")
            raise

    async def rollback(self):
        await self.session.rollback()

    async def get_by_id(self, entity_id: int):
        return await self.session.get(self.model, entity_id)

    async def get_all(self):
        result = await self.session.execute(select(self.model))
        return result.scalars().all()

    async def create(self, data: dict, commit: bool = True):
        try:
            new_entity = self.model(**data)
            self.session.add(new_entity)
            await self.session.flush()
            if commit:
                await self.commit()
            await self.session.refresh(new_entity)
            return new_entity
        except Exception as e:
            self.logger.error(message=f"Error while creating entity: {e}")
            return None

    async def update(self, entity_id: int, data: dict, commit: bool = True):
        try:
            entity = await self.get_by_id(entity_id)
            if not entity:
                return None
            for key, value in data.items():
                setattr(entity, key, value)
            await self.session.flush()
            if commit:
                await self.commit()
            await self.session.refresh(entity)
            return entity
        except Exception as e:
            self.logger.error(message=f"Error while updating entity: {e}")
            return None

    async def delete(self, entity_id: int, commit: bool = True):
        try:
            entity = await self.get_by_id(entity_id)
            if not entity:
                return None
            await self.session.delete(entity)
            await self.session.flush()
            if commit:
                await self.commit()
            return True
        except Exception as e:
            self.logger.error(message=f"Error while deleting entity: {e}")
            return False

    async def begin_transaction(self):
        return await self.session.begin()

    async def load(self, data: dict):
        try:
            new_entity = self.model(**data)
            return new_entity
        except Exception as e:
            self.logger.error(message=f"Error while loading entity: {e}")
            return None

    async def create_all(self, models, commit: bool = True):
        try:
            self.session.add_all(models)
            await self.session.flush()
            if commit:
                await self.commit()
            for model in models:
                await self.session.refresh(model)
            return models
        except Exception as e:
            self.logger.error(message=f"Error while saving entities: {e}")
            return None

    async def get_by_field(self, field: str, value):
        stmt = select(self.model).where(getattr(self.model, field) == value)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def filter_by(self, **kwargs):
        stmt = select(self.model).filter_by(**kwargs)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete_entity(self, entity, commit: bool = True):
        try:
            await self.session.delete(entity)
            await self.session.flush()
            if commit:
                await self.commit()
            return True
        except Exception as e:
            await self.rollback()
            self.logger.error(message=f"Error while deleting entity: {e}")
            return False

    async def get_paginated(self, limit: int = 20, offset: int = 0):
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def exists(self, entity_id: int):
        stmt = select(self.model).where(self.model.id == entity_id)
        result = await self.session.execute(stmt)
        return result.scalars().first() is not None

    async def update_by_id(self, entity_id: int, data: dict, commit: bool = True):
        stmt = (
            update(self.model)
            .where(self.model.id == entity_id)
            .values(**data)
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(stmt)
        if commit:
            await self.commit()
        return await self.get_by_id(entity_id)            
