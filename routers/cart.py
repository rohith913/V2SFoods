from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from urllib.parse import quote
from decimal import Decimal

from database import get_db
from models import CartMaster, ItemMaster

router = APIRouter(prefix="/cart", tags=["Cart"])
templates = Jinja2Templates(directory="templates")


def redirect_to_user_login(request: Request):
    next_url = quote(str(request.url.path))
    return RedirectResponse(
        f"/user/login?next={next_url}",
        status_code=302
    )


@router.get("/")
def cart_page(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("user_id"):
        return redirect_to_user_login(request)

    cart_items = db.query(CartMaster).filter(
        CartMaster.user_id == request.session.get("user_id")
    ).all()

    total = Decimal("0.00")

    for cart in cart_items:
        price = Decimal(str(cart.item.price or 0))
        selected_kg = Decimal(str(cart.selected_kg or 0.5))
        qty = Decimal(str(cart.qty or 1))

        total += price * selected_kg * qty

    return templates.TemplateResponse(
        request=request,
        name="cart.html",
        context={
            "cart_items": cart_items,
            "total": total
        }
    )


@router.get("/add/{item_id}")
def add_to_cart(
    item_id: int,
    request: Request,
    db: Session = Depends(get_db),
    kg: float = 0.5
):
    if not request.session.get("user_id"):
        return redirect_to_user_login(request)

    user_id = request.session.get("user_id")

    # Clamp kg to valid values
    if kg not in [0.5, 1.0]:
        kg = 0.5

    item = db.query(ItemMaster).filter(
        ItemMaster.id == item_id,
        ItemMaster.status == "ACTIVE"
    ).first()

    if not item:
        return RedirectResponse("/products", status_code=302)

    existing = db.query(CartMaster).filter(
        CartMaster.user_id == user_id,
        CartMaster.item_id == item_id
    ).first()

    if existing:
        existing.qty = (existing.qty or 1) + 1
        existing.selected_kg = Decimal(str(kg))
    else:
        cart = CartMaster(
            user_id=user_id,
            item_id=item_id,
            qty=1,
            selected_kg=Decimal(str(kg))
        )
        db.add(cart)

    db.commit()

    return RedirectResponse("/cart/", status_code=302)


@router.get("/kg/{cart_id}/{kg}")
def update_cart_kg(
    cart_id: int,
    kg: float,
    request: Request,
    db: Session = Depends(get_db)
):
    if not request.session.get("user_id"):
        return redirect_to_user_login(request)

    allowed_kgs = [
        0.5, 1, 1.5,
        2, 2.5, 3,
        3.5, 4, 4.5, 5
    ]

    if kg not in allowed_kgs:
        return RedirectResponse("/cart/", status_code=302)

    cart = db.query(CartMaster).filter(
        CartMaster.id == cart_id,
        CartMaster.user_id == request.session.get("user_id")
    ).first()

    if cart:
        cart.selected_kg = Decimal(str(kg))
        db.commit()

    return RedirectResponse("/cart/", status_code=302)


@router.get("/increase/{cart_id}")
def increase_qty(
    cart_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    if not request.session.get("user_id"):
        return redirect_to_user_login(request)

    cart = db.query(CartMaster).filter(
        CartMaster.id == cart_id,
        CartMaster.user_id == request.session.get("user_id")
    ).first()

    if cart:
        cart.qty = (cart.qty or 1) + 1
        db.commit()

    return RedirectResponse("/cart/", status_code=302)


@router.get("/decrease/{cart_id}")
def decrease_qty(
    cart_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    if not request.session.get("user_id"):
        return redirect_to_user_login(request)

    cart = db.query(CartMaster).filter(
        CartMaster.id == cart_id,
        CartMaster.user_id == request.session.get("user_id")
    ).first()

    if cart:
        if cart.qty and cart.qty > 1:
            cart.qty -= 1
            db.commit()
        else:
            db.delete(cart)
            db.commit()

    return RedirectResponse("/cart/", status_code=302)


@router.get("/remove/{cart_id}")
def remove_cart(
    cart_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    if not request.session.get("user_id"):
        return redirect_to_user_login(request)

    cart = db.query(CartMaster).filter(
        CartMaster.id == cart_id,
        CartMaster.user_id == request.session.get("user_id")
    ).first()

    if cart:
        db.delete(cart)
        db.commit()

    return RedirectResponse("/cart/", status_code=302)