from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime
from urllib.parse import quote

from database import get_db
from models import CartMaster, OrderMaster, OrderDetail

router = APIRouter(prefix="/order", tags=["Order"])


def redirect_to_user_login(request: Request):
    next_url = quote(str(request.url.path))
    return RedirectResponse(
        f"/user/login?next={next_url}",
        status_code=302
    )


@router.get("/booking")
def booking_order(
    request: Request,
    db: Session = Depends(get_db)
):
    if not request.session.get("user_id"):
        return redirect_to_user_login(request)
    user_id = request.session.get("user_id")

    cart_items = db.query(CartMaster).filter(
        CartMaster.user_id == user_id
    ).all()

    if not cart_items:
        return RedirectResponse("/cart/", status_code=302)

    total_amount = 0

    for cart in cart_items:
        total_amount += float(cart.item.price) * cart.qty

    order_no = "ORD" + datetime.now().strftime("%Y%m%d%H%M%S")

    order = OrderMaster(
        order_no=order_no,
        user_id=user_id,
        total_amount=total_amount,
        status="BOOKED"
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    for cart in cart_items:
        amount = float(cart.item.price) * cart.qty

        detail = OrderDetail(
            order_id=order.id,
            item_id=cart.item_id,
            qty=cart.qty,
            price=cart.item.price,
            amount=amount
        )

        db.add(detail)

    for cart in cart_items:
        db.delete(cart)

    db.commit()

    return RedirectResponse("/user/orders", status_code=302)