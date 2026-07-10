from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
from urllib.parse import quote
from decimal import Decimal
from database import get_db
from models import CartMaster, OrderMaster, OrderDetail, UserMaster

router = APIRouter(prefix="/order", tags=["Order"])
templates = Jinja2Templates(directory="templates")


def redirect_to_user_login(request: Request):
    next_url = quote(str(request.url.path))
    return RedirectResponse(f"/user/login?next={next_url}", status_code=302)


def generate_invoice_no(db: Session) -> str:
    """Generate sequential invoice number like INV-2024-0001"""
    year = datetime.now().year
    prefix = f"INV-{year}-"
    # Count existing invoices this year
    count = db.query(OrderMaster).filter(
        OrderMaster.invoice_no.like(f"{prefix}%")
    ).count()
    return f"{prefix}{str(count + 1).zfill(4)}"


@router.get("/checkout")
def checkout_page(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("user_id"):
        return redirect_to_user_login(request)

    user_id = request.session.get("user_id")
    cart_items = db.query(CartMaster).filter(CartMaster.user_id == user_id).all()

    if not cart_items:
        return RedirectResponse("/cart/", status_code=302)

    user = db.query(UserMaster).filter(UserMaster.id == user_id).first()

    total = Decimal("0.00")
    for cart in cart_items:
        price = Decimal(str(cart.item.price or 0))
        selected_kg = Decimal(str(cart.selected_kg or 0.5))
        qty = Decimal(str(cart.qty or 1))
        total += price * selected_kg * qty

    return templates.TemplateResponse(
        request=request,
        name="checkout.html",
        context={
            "cart_items": cart_items,
            "total": total,
            "user_name": user.username if user else "",
            "user_mobile": user.mobile if user else "",
        }
    )


@router.post("/place")
async def place_order(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("user_id"):
        return redirect_to_user_login(request)
    user_id = request.session.get("user_id")

    form = await request.form()
    payment_method = form.get("payment_method", "cod")
    full_name = form.get("full_name", "")
    mobile = form.get("mobile", "")
    address = form.get("address", "")
    city = form.get("city", "")
    state = form.get("state", "Tamil Nadu")
    pincode = form.get("pincode", "")

    cart_items = db.query(CartMaster).filter(CartMaster.user_id == user_id).all()
    if not cart_items:
        return RedirectResponse("/cart/", status_code=302)

    # ── FIX: calculate total using selected_kg (matching checkout) ──
    total_amount = Decimal("0.00")
    for c in cart_items:
        price = Decimal(str(c.item.price or 0))
        selected_kg = Decimal(str(c.selected_kg or 0.5))
        qty = Decimal(str(c.qty or 1))
        total_amount += price * selected_kg * qty

    order_no = "ORD" + datetime.now().strftime("%Y%m%d%H%M%S")
    invoice_no = generate_invoice_no(db)

    order = OrderMaster(
        order_no=order_no,
        invoice_no=invoice_no,
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
        price = Decimal(str(cart.item.price or 0))
        selected_kg = Decimal(str(cart.selected_kg or 0.5))
        qty = Decimal(str(cart.qty or 1))
        amount = price * selected_kg * qty

        detail = OrderDetail(
            order_id=order.id,
            item_id=cart.item_id,
            qty=int(cart.qty or 1),
            selected_kg=selected_kg,
            price=price,
            amount=amount
        )
        db.add(detail)

    for cart in cart_items:
        db.delete(cart)

    db.commit()

    return templates.TemplateResponse(request=request, name="order_success.html", context={
        "order_no": order_no,
        "invoice_no": invoice_no,
        "total_amount": float(total_amount),
        "payment_method": payment_method.upper().replace("_", " "),
    })


@router.get("/booking")
def booking_order(request: Request):
    if not request.session.get("user_id"):
        return redirect_to_user_login(request)
    return RedirectResponse("/order/checkout", status_code=302)


@router.get("/invoice/{order_id}")
def view_invoice(order_id: int, request: Request, db: Session = Depends(get_db)):
    """Printable invoice page – accessible by user or admin."""
    user_id = request.session.get("user_id")
    admin_id = request.session.get("admin_id")
    if not user_id and not admin_id:
        return redirect_to_user_login(request)

    order = db.query(OrderMaster).filter(OrderMaster.id == order_id).first()
    if not order:
        return RedirectResponse("/products", status_code=302)

    # Users can only see their own invoices
    if user_id and order.user_id != user_id:
        return RedirectResponse("/user/orders", status_code=302)

    return templates.TemplateResponse(request=request, name="invoice.html", context={
        "order": order,
        "title": f"Invoice {order.invoice_no} – V2S Foods"
    })
