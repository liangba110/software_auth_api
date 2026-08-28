from sqlalchemy import Column, Integer, String, DateTime, SmallInteger
from app.db.base import Base
from datetime import datetime

class App(Base):
    __tablename__ = "app"

    id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(String(32), unique=True, nullable=False, index=True)
    app_key = Column(String(64), nullable=False)
    app_name = Column(String(100), nullable=False)
    logo_url = Column(String(255), nullable=True)
    notify_url = Column(String(255), nullable=True)
    status = Column(SmallInteger, default=1, comment="1启用 0禁用")
    create_time = Column(DateTime, default=datetime.now)
