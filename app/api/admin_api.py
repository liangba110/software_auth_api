import secrets
import os
"""
softapi 管理后台 API
管理员认证: Bearer Token (JWT, admin secret)
"""
import hashlib, time
from fastapi import APIRouter, Depends, Request, Header
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.admin import AdminUser
from app.models.app import App
from app.models.app_user import AppUser
from app.models.app_order import AppOrder
from app.models.app_vip_log import AppVipLog
from app.common.response import success, fail
from app.common.security import hash_password, verify_password
from app.common.limiter import limiter
from app.config.settings import settings
from datetime import datetime, timedelta

router = APIRouter()

ADMIN_SECRET = os.getenv("ADMIN_SECRET", "") or (settings.JWT_SECRET + '_admin')


def _admin_token(user_id: int) -> str:
    import jwt
    payload = {"admin_id": user_id, "exp": datetime.utcnow() + timedelta(hours=12)}
    return jwt.encode(payload, ADMIN_SECRET, algorithm="HS256")


def require_admin(authorization: str = Header(default=""), db: Session = Depends(get_db)):
    from fastapi import HTTPException
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    import jwt
    try:
        payload = jwt.decode(authorization[7:], ADMIN_SECRET, algorithms=["HS256"])
        admin = db.query(AdminUser).filter(AdminUser.id == payload.get("admin_id")).first()
        if not admin:
            raise HTTPException(status_code=401, detail="管理员不存在")
        return admin
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="登录已过期")
    except Exception:
        raise HTTPException(status_code=401, detail="token无效")


def _check_admin(admin):
    if not admin:
        raise Exception("UNAUTHORIZED")


# ============ 登录 ============
@router.post("/login")
@limiter.limit("5/minute")
async def admin_login(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    username = (body.get('username') or '').strip()
    password = body.get('password', '')
    admin = db.query(AdminUser).filter(AdminUser.username == username).first()
    if not admin or not verify_password(password, admin.password):
        return fail(code=401, msg="用户名或密码错误")
    return success(data={"token": _admin_token(admin.id), "username": admin.username}, msg="登录成功")


# ============ 总览统计 ============
@router.get("/stats")
async def admin_stats(authorization: str = Header(default=""), db: Session = Depends(get_db)):
    admin = require_admin(authorization, db)
    apps = db.query(App).count()
    users = db.query(AppUser).count()
    orders = db.query(AppOrder).count()
    paid = db.query(AppOrder).filter(AppOrder.status == 1).count()
    today = datetime.now().date()
    today_amount = db.query(AppOrder).filter(AppOrder.status == 1, AppOrder.pay_time >= datetime(today.year, today.month, today.day)).all()
    total = sum(float(o.amount) for o in today_amount)
    return success(data={
        "apps": apps, "users": users, "orders": orders,
        "paid_orders": paid, "today_amount": round(total, 2),
        "today_orders": len(today_amount)
    })


# ============ 软件管理 ============
@router.get("/apps")
async def admin_apps(authorization: str = Header(default=""), db: Session = Depends(get_db)):
    admin = require_admin(authorization, db)
    apps = db.query(App).order_by(App.id.desc()).all()
    return success(data=[{
        "id": a.id, "app_id": a.app_id, "app_name": a.app_name,
        "notify_url": a.notify_url, "logo_url": a.logo_url,
        "status": a.status, "create_time": a.create_time.strftime("%Y-%m-%d %H:%M") if a.create_time else None,
        "price_1": float(a.price_1 or 9.9), "price_2": float(a.price_2 or 29.9),
        "price_3": float(a.price_3 or 199.9), "price_4": float(a.price_4 or 520.0)
    } for a in apps])


@router.post("/apps")
async def admin_app_create(request: Request, authorization: str = Header(default=""), db: Session = Depends(get_db)):
    admin = require_admin(authorization, db)
    body = await request.json()
    app_name = (body.get('app_name') or '').strip()
    if not app_name:
        return fail(msg="软件名称必填")
    app_id = 'APP' + secrets.token_hex(8)
    app_key = secrets.token_hex(16)
    from app.crud.app_crud import create_app
    app = create_app(db, app_id, app_key, app_name,
                     logo_url=(body.get('logo_url') or '').strip() or None,
                     notify_url=(body.get('notify_url') or '').strip() or None)
    # 设置自定义价格
    for i in (1, 2, 3, 4):
        v = body.get(f'price_{i}')
        if v is not None:
            setattr(app, f'price_{i}', float(v))
    db.commit()
    return success(data={"app_id": app.app_id, "app_key": app.app_key}, msg="软件创建成功")


@router.put("/apps/{app_id}")
async def admin_app_update(app_id: str, request: Request, authorization: str = Header(default=""), db: Session = Depends(get_db)):
    admin = require_admin(authorization, db)
    app = db.query(App).filter(App.app_id == app_id).first()
    if not app:
        return fail(code=404, msg="软件不存在")
    body = await request.json()
    for field in ('app_name', 'notify_url', 'logo_url'):
        if field in body:
            setattr(app, field, (body[field] or '').strip() or None)
    if 'status' in body:
        app.status = int(body['status'])
    for i in (1, 2, 3, 4):
        key = f'price_{i}'
        if key in body and body[key] is not None:
            setattr(app, key, float(body[key]))
    db.commit()
    return success(msg="已保存")


@router.delete("/apps/{app_id}")
async def admin_app_delete(app_id: str, authorization: str = Header(default=""), db: Session = Depends(get_db)):
    admin = require_admin(authorization, db)
    app = db.query(App).filter(App.app_id == app_id).first()
    if not app:
        return fail(code=404, msg="软件不存在")
    # 检查有无用户/订单
    uc = db.query(AppUser).filter(AppUser.app_id == app_id).count()
    oc = db.query(AppOrder).filter(AppOrder.app_id == app_id).count()
    if uc > 0 or oc > 0:
        return fail(msg=f"该软件有 {uc} 用户 / {oc} 订单，不能删除，可禁用")
    db.delete(app)
    db.commit()
    return success(msg="已删除")


# ============ 用户管理 ============
@router.get("/users")
async def admin_users(app_id: str = "", keyword: str = "", page: int = 1, page_size: int = 20,
                      authorization: str = Header(default=""), db: Session = Depends(get_db)):
    admin = require_admin(authorization, db)
    q = db.query(AppUser)
    if app_id:
        q = q.filter(AppUser.app_id == app_id)
    if keyword:
        q = q.filter(AppUser.username.like(f'%{keyword}%'))
    total = q.count()
    users = q.order_by(AppUser.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    app_names = {a.app_id: a.app_name for a in db.query(App).all()}
    return success(data={
        "total": total, "page": page, "page_size": page_size,
        "list": [{
            "id": u.id, "app_id": u.app_id, "app_name": app_names.get(u.app_id, u.app_id),
            "username": u.username, "status": u.status, "vip_type": u.vip_type,
            "vip_expire_time": u.vip_expire_time.strftime("%Y-%m-%d %H:%M:%S") if u.vip_expire_time else None,
            "last_login_time": u.last_login_time.strftime("%Y-%m-%d %H:%M") if u.last_login_time else None,
            "create_time": u.create_time.strftime("%Y-%m-%d %H:%M") if u.create_time else None
        } for u in users]
    })


@router.put("/users/{user_id}")
async def admin_user_update(user_id: int, request: Request, authorization: str = Header(default=""), db: Session = Depends(get_db)):
    admin = require_admin(authorization, db)
    user = db.query(AppUser).filter(AppUser.id == user_id).first()
    if not user:
        return fail(code=404, msg="用户不存在")
    body = await request.json()
    old_vip, old_exp = user.vip_type, user.vip_expire_time

    if 'status' in body:
        user.status = int(body['status'])
    if 'vip_type' in body:
        user.vip_type = int(body['vip_type'])
    if 'vip_expire_time' in body:
        v = body['vip_expire_time']
        user.vip_expire_time = datetime.strptime(v, '%Y-%m-%d %H:%M:%S') if v else None
    db.commit()

    # 记录日志
    if body.get('log'):
        log = AppVipLog(app_id=user.app_id, user_id=user.id, username=user.username,
                        old_vip_type=old_vip, new_vip_type=user.vip_type,
                        old_expire_time=old_exp, new_expire_time=user.vip_expire_time,
                        operate_type=body.get('log'), operator=admin.username)
        db.add(log)
        db.commit()
    return success(msg="已保存")


# ============ 订单管理 ============
@router.get("/orders")
async def admin_orders(app_id: str = "", status: str = "", order_sn: str = "", page: int = 1, page_size: int = 20,
                       authorization: str = Header(default=""), db: Session = Depends(get_db)):
    admin = require_admin(authorization, db)
    q = db.query(AppOrder)
    if app_id:
        q = q.filter(AppOrder.app_id == app_id)
    if status != '' and status is not None:
        q = q.filter(AppOrder.status == int(status))
    if order_sn:
        q = q.filter(AppOrder.order_sn.like(f'%{order_sn}%'))
    total = q.count()
    orders = q.order_by(AppOrder.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    app_names = {a.app_id: a.app_name for a in db.query(App).all()}
    return success(data={
        "total": total, "page": page, "page_size": page_size,
        "list": [{
            "order_sn": o.order_sn, "app_id": o.app_id, "app_name": app_names.get(o.app_id, o.app_id),
            "user_id": o.user_id, "goods_type": o.goods_type, "amount": float(o.amount),
            "status": o.status, "pay_type": o.pay_type,
            "notify_status": o.notify_status,
            "pay_time": o.pay_time.strftime("%Y-%m-%d %H:%M:%S") if o.pay_time else None,
            "create_time": o.create_time.strftime("%Y-%m-%d %H:%M:%S") if o.create_time else None
        } for o in orders]
    })


# ============ 开通记录 ============
@router.get("/vip-logs")
async def admin_vip_logs(app_id: str = "", keyword: str = "", page: int = 1, page_size: int = 20,
                         authorization: str = Header(default=""), db: Session = Depends(get_db)):
    admin = require_admin(authorization, db)
    q = db.query(AppVipLog)
    if app_id:
        q = q.filter(AppVipLog.app_id == app_id)
    if keyword:
        q = q.filter(AppVipLog.username.like(f'%{keyword}%'))
    total = q.count()
    logs = q.order_by(AppVipLog.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    app_names = {a.app_id: a.app_name for a in db.query(App).all()}
    return success(data={
        "total": total, "page": page, "page_size": page_size,
        "list": [{
            "id": l.id, "app_id": l.app_id, "app_name": app_names.get(l.app_id, l.app_id),
            "user_id": l.user_id, "username": l.username, "order_sn": l.order_sn,
            "old_vip_type": l.old_vip_type, "new_vip_type": l.new_vip_type,
            "old_expire_time": l.old_expire_time.strftime("%Y-%m-%d %H:%M:%S") if l.old_expire_time else None,
            "new_expire_time": l.new_expire_time.strftime("%Y-%m-%d %H:%M:%S") if l.new_expire_time else None,
            "operate_type": l.operate_type, "operator": l.operator,
            "create_time": l.create_time.strftime("%Y-%m-%d %H:%M:%S") if l.create_time else None
        } for l in logs]
    })


# ============ 修改密码 ============
@router.put("/password")
async def admin_password(request: Request, authorization: str = Header(default=""), db: Session = Depends(get_db)):
    admin = require_admin(authorization, db)
    body = await request.json()
    old_pwd = body.get('old_password', '')
    new_pwd = body.get('new_password', '')
    if not verify_password(old_pwd, admin.password):
        return fail(msg="原密码错误")
    if len(new_pwd) < 8:
        return fail(msg="新密码至少8位")
    admin.password = hash_password(new_pwd)
    db.commit()
    return success(msg="密码已修改")
