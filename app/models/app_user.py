from sqlalchemy import Column, Integer, String, DateTime, SmallInteger
from app.db.base import Base
from datetime import datetime

class AppUser(Base):
    __tablename__ = "app_user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(String(32), nullable=False, index=True)
    username = Column(String(50), nullable=False)
    password = Column(String(255), nullable=False)
    status = Column(SmallInteger, default=1, comment="1正常 0封禁")
    vip_type = Column(SmallInteger, default=0, comment="0普通 1日卡 2月卡 3年卡 4永久")
    vip_expire_time = Column(DateTime, nullable=True)
    last_login_time = Column(DateTime, nullable=True)
    create_time = Column(DateTime, default=datetime.now)
