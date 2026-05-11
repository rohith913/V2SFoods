from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import get_db
from models import AdminMaster, OrderMaster, UserMaster, ItemMaster

router = APIRouter(prefix="/admin", tags=["Admin"])

templates = Jinja2Templates(directory="templates")



@router.get("/register")
def admin_register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin_register.html",
        context={}
    )


@router.post("/register")
def admin_register(
    request: Request,
    admin_name: str = Form(...),
    mobile: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    existing = db.query(AdminMaster).filter(
        AdminMaster.email == email
    ).first()

    if existing:
        return templates.TemplateResponse(
            request=request,
            name="admin_register.html",
            context={
                "error": "Admin email already registered"
            }
        )

   

    admin = AdminMaster(
        admin_name=admin_name,
        mobile=mobile,
        email=email,
        password=password,
        role="ADMIN",
        status="ACTIVE"
    )

    db.add(admin)
    db.commit()

    return RedirectResponse("/admin/login", status_code=302)


@router.get("/login")
def admin_login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin_login.html",
        context={}
    )


@router.post("/login")
def admin_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    admin = db.query(AdminMaster).filter(
        AdminMaster.email == email,
        AdminMaster.status == "ACTIVE"
    ).first()

    if password != admin.password:
        return templates.TemplateResponse(
            request=request,
            name="admin_login.html",
            context={
                "error": "Invalid email or password"
            }
        )
    

    request.session["admin_id"] = admin.id
    request.session["admin_email"] = admin.email
    request.session["admin_name"] = admin.admin_name
    request.session["role"] = "ADMIN"

    return RedirectResponse("/admin/dashboard", status_code=302)


@router.get("/dashboard")
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("admin_id"):
        return RedirectResponse("/admin/login")

    item_count = db.query(ItemMaster).count()
    user_count = db.query(UserMaster).count()
    order_count = db.query(OrderMaster).count()

    return templates.TemplateResponse(
        request=request,
        name="admin_dashboard.html",
        context={
            "item_count": item_count,
            "user_count": user_count,
            "order_count": order_count
        }
    )


@router.get("/billing-summary")
def billing_summary(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("admin_id"):
        return RedirectResponse("/admin/login")

    orders = db.query(OrderMaster).order_by(
        OrderMaster.id.desc()
    ).all()

    total_amount = sum(float(order.total_amount) for order in orders)

    return templates.TemplateResponse(
        request=request,
        name="billing_summary.html",
        context={
            "orders": orders,
            "total_amount": total_amount
        }
    )


@router.get("/all-orders")
def all_orders(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("admin_id"):
        return RedirectResponse("/admin/login")

    orders = db.query(OrderMaster).order_by(
        OrderMaster.id.desc()
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="all_orders.html",
        context={
            "orders": orders
        }
    )


@router.get("/logout")
def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse("/admin/login")