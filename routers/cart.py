from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from urllib.parse import quote

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

    total = 0

    for cart in cart_items:
        total += float(cart.item.price) * cart.qty

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
    db: Session = Depends(get_db)
):
    if not request.session.get("user_id"):
        return redirect_to_user_login(request)

    user_id = request.session.get("user_id")

    item = db.query(ItemMaster).filter(
        ItemMaster.id == item_id,
        ItemMaster.status == "ACTIVE"
    ).first()       

    if not item:
        return RedirectResponse("/products", status_code=302)

    existing_cart = db.query(CartMaster).filter(
        CartMaster.user_id == user_id,
        CartMaster.item_id == item_id
    ).first()

    if existing_cart:
        existing_cart.qty += 1
    else:
        cart = CartMaster(
            user_id=user_id,
            item_id=item_id,
            qty=1
        )
        db.add(cart)

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
