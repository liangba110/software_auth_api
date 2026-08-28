from sqlalchemy import Column, Integer, String, DateTime, SmallInteger, Numeric
from app.db.base import Base
from datetime import datetime

class AppOrder(Base):
    __tablename__ = "app_order"

    id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(String(32), nullable=False, index=True)
    order_sn = Column(String(64), unique=True, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    pay_type = Column(String(20), nullable=False, comment="wechat")
    goods_type = Column(SmallInteger, nullable=False, comment="1日卡 2月卡 3年卡 4永久")
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(SmallInteger, default=0, comment="0待支付 1已支付 2已过期")
    transaction_id = Column(String(128), nullable=True)
    pay_time = Column(DateTime, nullable=True)
    notify_status = Column(SmallInteger, default=0, comment="0未通知 1已通知")
    create_time = Column(DateTime, default=datetime.now)
