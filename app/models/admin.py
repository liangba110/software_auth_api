from sqlalchemy import Column, Integer, String, DateTime
from app.db.base import Base
from datetime import datetime

class AdminUser(Base):
    __tablename__ = "admin_user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    create_time = Column(DateTime, default=datetime.now)
