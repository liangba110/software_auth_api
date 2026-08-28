from sqlalchemy.orm import Session
from app.models.app import App
from app.models.app_user import AppUser
from app.models.app_order import AppOrder
from datetime import datetime

# ============ App（软件）============
def get_app_by_id(db: Session, app_id: str):
    return db.query(App).filter(App.app_id == app_id).first()

def create_app(db: Session, app_id: str, app_key: str, app_name: str, logo_url: str = None, notify_url: str = None):
    app = App(app_id=app_id, app_key=app_key, app_name=app_name,
              logo_url=logo_url, notify_url=notify_url)
    db.add(app)
    db.commit()
    db.refresh(app)
    return app

# ============ AppUser（软件用户）============
def get_app_user(db: Session, app_id: str, username: str):
    return db.query(AppUser).filter(AppUser.app_id == app_id, AppUser.username == username).first()

def create_app_user(db: Session, app_id: str, username: str, password_hash: str):
    u = AppUser(app_id=app_id, username=username, password=password_hash)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

def get_app_user_by_id(db: Session, app_id: str, user_id: int):
    return db.query(AppUser).filter(AppUser.app_id == app_id, AppUser.id == user_id).first()

def update_app_user_vip(db: Session, user_id: int, vip_type: int, expire_time):
    u = db.query(AppUser).filter(AppUser.id == user_id).first()
    if u:
        u.vip_type = vip_type
        u.vip_expire_time = expire_time
        db.commit()
        return True
    return False

# ============ AppOrder（软件订单）============
def create_app_order(db: Session, app_id: str, order_sn: str, user_id: int, pay_type: str, goods_type: int, amount: float):
    o = AppOrder(app_id=app_id, order_sn=order_sn, user_id=user_id,
                 pay_type=pay_type, goods_type=goods_type, amount=amount)
    db.add(o)
    db.commit()
    db.refresh(o)
    return o

def get_app_order_by_sn(db: Session, order_sn: str):
    return db.query(AppOrder).filter(AppOrder.order_sn == order_sn).first()

def update_app_order_paid(db: Session, order_sn: str, transaction_id: str):
    o = get_app_order_by_sn(db, order_sn)
    if o and o.status == 0:
        o.status = 1
        o.pay_time = datetime.now()
        o.transaction_id = transaction_id
        db.commit()
        return True
    return False

def mark_app_order_notified(db: Session, order_sn: str):
    o = get_app_order_by_sn(db, order_sn)
    if o:
        o.notify_status = 1
        db.commit()

def list_app_orders(db: Session, app_id: str, user_id: int, page: int = 1, page_size: int = 20):
    return db.query(AppOrder).filter(AppOrder.app_id == app_id, AppOrder.user_id == user_id) \
        .order_by(AppOrder.create_time.desc()).offset((page-1)*page_size).limit(page_size).all()
