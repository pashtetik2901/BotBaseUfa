from sqlalchemy import select, and_
from bot.database.models import User, Report, FFExecuter, Response
from bot.database.repositories.base import BaseRepository
from typing import Any


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    async def get_by_telegram_id(self, telegram_id: int):
        stmt = select(self.model).filter_by(telegram_id=telegram_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_username(self, username: str):
        stmt = select(self.model).filter(self.model.username.ilike(username))
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    async def add_user(self, telegram_id: int, username: str):
        user = User(telegram_id, username)
        self.session.add(user)
        await self.session.commit()


class ReportRepository(BaseRepository):
    def __init__(self):
        super().__init__(Report)

    async def delete_report(self, report_id: str):
        report: Report = await self.get_one_report(report_id)
        if report:
            data = report.to_dict()
            await self.session.delete(report)
            await self.session.commit()
            return data

    async def update_status(self, report_id: int, new_status: str):
        report: Report = await self.get_one_report(report_id)
        if report:
            report.status = new_status
            data = report.to_dict()
            await self.session.commit()
            return data

    async def get_one_report(self, report_id: str):
        stmt = select(self.model).where(self.model.id == report_id)
        result = await self.session.execute(stmt)
        return result.scalar()

    async def get_my_report(self, seller_id: int):
        stmt = select(self.model).where(self.model.seller_id == seller_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_admin_report(self):
        stmt = select(self.model).where(self.model.status == 'Модерация')
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add_report(self, data: dict[str, Any]):
        report = Report(
            data.get('seller_id'),
            data.get('seller_username'),
            data.get('location'),
            data.get('storage'),
            data.get('category'),
            data.get('size'),
            data.get('count'),
            data.get('attachments'),
            data.get('pack'),
            data.get('comment'),
            data.get('status')
        )
        self.session.add(report)
        await self.session.commit()

    async def update_message_id(self, report_id: int, message_id: int):
        report = await self.get_one_report(report_id)
        if report:
            report.message_id = message_id
            await self.session.commit()


# class AdminRepository(BaseRepository):
#     def __init__(self):
#         super().__init__(Admin)

#     async def sign_up(self, admin_id: int):
#         admin = Admin(admin_id)
#         self.session.add(admin)
#         await self.session.commit()


#     async def get_admin(self, admin_id: int) -> Any | None:
#         stmt = select(self.model).where(self.model.admin_id == admin_id)
#         result = await self.session.execute(stmt)
#         return result.scalar()
    
class FFExecuterRepository(BaseRepository):
    def __init__(self):
        super().__init__(FFExecuter)

    async def add_ff_executer(self, username: str):
        ff = FFExecuter(username, 'free')
        self.session.add(ff)
        await self.session.commit()

    async def get_executer(self, username: str):
        stmt = select(self.model).where(self.model.username == f'@{username}')
        result = await self.session.execute(stmt)
        return result.scalar()

class ResponseRepository(BaseRepository):
    def __init__(self):
        super().__init__(Response)

    async def get_one_response(self, response_id: int):
        stmt = select(self.model).where(self.model.id == response_id)
        result = await self.session.execute(stmt)
        return result.scalar()
    
    async def update_status_pro(self, report_id: str, seller_id: int, status: str):
        stmt = select(self.model).where(and_(
            self.model.report_id == report_id,
            self.model.status == 'Принято',
            self.model.seller_id == seller_id
        ))
        result = await self.session.execute(stmt)
        response = result.scalar()
        if response:
            new_response = await self.update_status(response.id, status)
            return new_response

    
    async def update_status(self, response_id: int, status: str):
        response: Response = await self.get_one_response(response_id)
        if response:
            response.status = status
            await self.session.commit()
        response: Response = await self.get_one_response(response_id)
        return response
    
    async def disagree_response(self, response_id: int):
        response: Response = await self.get_one_response(response_id)
        if response:
            stmt = select(self.model).where(and_(
                self.model.report_id == response.report_id,
                self.model.id != response.id
            ))
            result = await self.session.execute(stmt)
            return result.scalars().all()
            


    async def add_response(self, report_id: str, seller_id: int, ff_id: int):
        response = Response(report_id, seller_id, ff_id, 'Отправлен')
        self.session.add(response)
        await self.session.flush()
        response_id = response.id
        await self.session.commit()
        return response_id
            
        
    async def get_all_my_response(self, ff_id: int):
        stmt = select(self.model).where(self.model.ff_id == ff_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

