from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
from urllib.parse import quote

from database import get_db
from models import CartMaster, OrderMaster, OrderDetail, UserMaster

router = APIRouter(prefix="/order", tags=["Order"])
templates = Jinja2Templates(directory="templates")


def redirect_to_user_login(request: Request):
    next_url = quote(str(request.url.path))
    return RedirectResponse(f"/user/login?next={next_url}", status_code=302)


@router.get("/checkout")
def checkout_page(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("user_id"):
        return redirect_to_user_login(request)
    user_id = request.session.get("user_id")
    cart_items = db.query(CartMaster).filter(CartMaster.user_id == user_id).all()
    if not cart_items:
        return RedirectResponse("/cart/", status_code=302)

    user = db.query(UserMaster).filter(UserMaster.id == user_id).first()
    total = sum(float(c.item.price) * c.qty for c in cart_items)

    return templates.TemplateResponse(request=request, name="checkout.html", context={
        "cart_items": cart_items,
        "total": total,
        "user_name": user.username if user else "",
        "user_mobile": user.mobile if user else "",
    })


@router.post("/place")
async def place_order(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("user_id"):
        return redirect_to_user_login(request)
    user_id = request.session.get("user_id")

    form = await request.form()
    payment_method = form.get("payment_method", "cod")
    full_name  = form.get("full_name", "")
    mobile     = form.get("mobile", "")
    address    = form.get("address", "")
    city       = form.get("city", "")
    state      = form.get("state", "Tamil Nadu")
    pincode    = form.get("pincode", "")

    cart_items = db.query(CartMaster).filter(CartMaster.user_id == user_id).all()
    if not cart_items:
        return RedirectResponse("/cart/", status_code=302)

    total_amount = sum(float(c.item.price) * c.qty for c in cart_items)
    order_no = "ORD" + datetime.now().strftime("%Y%m%d%H%M%S")

    order = OrderMaster(
        order_no=order_no,
        user_id=user_id,
        total_amount=total_amount,
        status="BOOKED",
        cust_name=full_name,
        cust_mobile=mobile,
        cust_address=address,
        cust_city=city,
        cust_state=state,
        cust_pincode=pincode,
        payment_method=payment_method.upper().replace("_", " ")
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    for cart in cart_items:
        detail = OrderDetail(
            order_id=order.id,
            item_id=cart.item_id,
            qty=cart.qty,
            price=cart.item.price,
            amount=float(cart.item.price) * cart.qty
        )
        db.add(detail)

    for cart in cart_items:
        db.delete(cart)

    db.commit()

    return templates.TemplateResponse(request=request, name="order_success.html", context={
        "order_no": order_no,
        "total_amount": total_amount,
        "payment_method": payment_method.upper().replace("_", " "),
    })


@router.get("/booking")
def booking_order(request: Request):
    if not request.session.get("user_id"):
        return redirect_to_user_login(request)
    return RedirectResponse("/order/checkout", status_code=302)
