from sqlalchemy import Column, Integer, String, JSON, Boolean, DateTime, func
from bot.database.db import Base
import uuid

def generate_uid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, nullable=True)

    def __init__(self, tg_id: int, username: str):
        self.telegram_id = tg_id
        self.username = username

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id})>"
    
class Report(Base):
    __tablename__ = 'report'

    id = Column(String, primary_key=True, default=generate_uid)
    seller_id = Column(Integer, nullable=False)
    seller_username = Column(String, nullable=True)
    message_id = Column(Integer, nullable=True)
    location = Column(String, nullable=False)
    storage = Column(String, nullable=False)
    category = Column(String, nullable=False)
    size = Column(String, nullable=False)
    count = Column(Integer, nullable=False)
    attachments = Column(JSON, nullable=True)
    pack = Column(String, nullable=False)
    comment = Column(String, nullable=True)
    status = Column(String, nullable=False)

    
    def __init__(self, seller_id: int, seller_username: str | None, location: str, storage: str,category: str, size: str,
                    count: int, attachments: dict | None, pack: str,
                    comment: str | None, status: str, message_id = None):
            self.seller_id = seller_id
            self.seller_username = seller_username
            self.message_id = message_id
            self.location = location
            self.storage = storage
            self.category = category
            self.size = size
            self.count = count
            self.attachments = attachments
            self.pack = pack
            self.comment = comment
            self.status = status

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "seller_id": self.seller_id,
            'seller_username': self.seller_username,
            'message_id': self.message_id,
            "location": self.location,
            "storage": self.storage,
            "category": self.category,
            "size": self.size,
            "count": self.count,
            "attachments": self.attachments,
            "pack": self.pack,
            "comment": self.comment,
            "status": self.status,
        }
    
# class Admin(Base):
#     __tablename__ = 'admin'

#     id = Column(Integer, primary_key=True)
#     admin_id = Column(Integer, nullable=False)

#     def __init__(self, admin_id: int):
#          self.admin_id = admin_id

class Response(Base):
    __tablename__ = 'response'

    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, nullable=False) 
    seller_id = Column(Integer, nullable=False)#telegram id
    ff_id = Column(Integer, nullable=False)
    status = Column(String, nullable=True)

    def __init__(self, report_id: str, seller_id: int, ff_id: int, status: str):
        self.report_id = report_id
        self.seller_id = seller_id
        self.ff_id = ff_id
        self.status = status

class FFExecuter(Base):
    __tablename__ = 'ff_executer'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    status = Column(String, nullable=False)
    create_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __init__(self, username: str, status: str):
        self.username = username
        self.status = status

    