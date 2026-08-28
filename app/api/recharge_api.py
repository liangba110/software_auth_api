from fastapi import APIRouter, Depends, Form
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
async def pay_callback(
    out_trade_no: str = Form(...),
    trade_no: str = Form(...),
    db: Session = Depends(get_db)
):
    ok, msg = recharge_callback_handle(db, out_trade_no, trade_no)
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
