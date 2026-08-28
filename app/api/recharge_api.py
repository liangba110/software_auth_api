from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.schemas.order_schema import CreateOrderSchema
from app.service.recharge_service import create_recharge_order, recharge_callback_handle
from app.common.response import success, fail
from app.common.security import parse_token

router = APIRouter()

@router.post("/create")
async def create_order(token: str, data: CreateOrderSchema, db: Session = Depends(get_db)):
    payload = parse_token(token)
    if not payload:
        return fail(code=401, msg="未登录")
    user_id = payload["user_id"]
    ok, res = create_recharge_order(db, user_id, data.goods_type, data.pay_type)
    if not ok:
        return fail(msg=res)
    return success(data=res)

@router.post("/callback")
async def pay_callback(request: Request, db: Session = Depends(get_db)):
    """统一支付网关回调（JSON: order_no/amount/status/timestamp + X-Pay-Token）"""
    # 验签：网关固定 Token 头
    token = request.headers.get("X-Pay-Token", "")
    if token != "huizhiyun_gateway_2026":
        return fail(msg="签名无效")
    body = await request.json()
    out_trade_no = body.get("order_no", "")
    status = body.get("status", 0)
    if status != 1 or not out_trade_no:
        return fail(msg="无效回调")
    ok, msg = recharge_callback_handle(db, out_trade_no, out_trade_no)
    if not ok:
        return fail(msg=msg)
    return success(msg=msg)

@router.get("/list")
async def order_list(token: str, db: Session = Depends(get_db)):
    from app.crud.order_crud import get_user_order_list
    payload = parse_token(token)
    if not payload:
        return fail(code=401, msg="未登录")
    list_data = get_user_order_list(db, payload["user_id"])
    return success(data=list_data)
