from sqlalchemy import Column, Integer, String, DateTime, SmallInteger
from app.db.base import Base
from datetime import datetime

class AppVipLog(Base):
    __tablename__ = "app_vip_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(String(32), nullable=False, index=True)
    user_id = Column(Integer, nullable=False)
    username = Column(String(50), nullable=True)
    order_sn = Column(String(64), nullable=True)
    old_vip_type = Column(SmallInteger, default=0)
    new_vip_type = Column(SmallInteger, default=0)
    old_expire_time = Column(DateTime, nullable=True)
    new_expire_time = Column(DateTime, nullable=True)
    operate_type = Column(String(50), nullable=True)
    operator = Column(String(50), nullable=True)
    create_time = Column(DateTime, default=datetime.now)
