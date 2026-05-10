from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
from models import ItemMaster

router = APIRouter(tags=["Item"])

templates = Jinja2Templates(directory="templates")


@router.get("/admin/item-master")
def item_master_page(request: Request):
    if not request.session.get("admin_id"):
        return RedirectResponse("/admin/login")

    return templates.TemplateResponse(
        request=request,
        name="item_master.html",
        context={}
    )


@router.post("/admin/item-master")
def add_item(
    request: Request,
    item_code: str = Form(...),
    item_name: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    stock_qty: int = Form(...),
    image_url: str = Form(""),
    status: str = Form("ACTIVE"),
    db: Session = Depends(get_db)
):
    if not request.session.get("admin_id"):
        return RedirectResponse("/admin/login")

    existing = db.query(ItemMaster).filter(
        ItemMaster.item_code == item_code
    ).first()

    if existing:
        return templates.TemplateResponse(
            request=request,
            name="item_master.html",
            context={
                "error": "Item code already exists"
            }
        )

    item = ItemMaster(
        item_code=item_code,
        item_name=item_name,
        description=description,
        category=category,
        price=price,
        stock_qty=stock_qty,
        image_url=image_url,
        status=status
    )

    db.add(item)
    db.commit()

    return RedirectResponse("/admin/item-list", status_code=302)


@router.get("/admin/item-list")
def admin_item_list(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("admin_id"):
        return RedirectResponse("/admin/login")

    items = db.query(ItemMaster).order_by(
        ItemMaster.id.desc()
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="item_list.html",
        context={
            "items": items
        }
    )


@router.get("/products")
def product_list(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("user_id"):
        return RedirectResponse("/user/login")

    items = db.query(ItemMaster).filter(
        ItemMaster.status == "ACTIVE"
    ).order_by(ItemMaster.id.desc()).all()

    return templates.TemplateResponse(
        request=request,
        name="product_list.html",
        context={
            "items": items
        }
    )