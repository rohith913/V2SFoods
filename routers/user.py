from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import get_db
from models import UserMaster, OrderMaster

router = APIRouter(prefix="/user", tags=["User"])

templates = Jinja2Templates(directory="templates")




@router.get("/register")
def user_register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="user_register.html",
        context={}
    )


@router.post("/register")
def user_register(
    request: Request,
    username: str = Form(...),
    mobile: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    existing = db.query(UserMaster).filter(
        UserMaster.email == email
    ).first()

    if existing:
        return templates.TemplateResponse(
            request=request,
            name="user_register.html",
            context={
                "error": "Email already registered"
            }
        )

    

    user = UserMaster(
        username=username,
        mobile=mobile,
        email=email,
        password=password,
        status="ACTIVE"
    )

    db.add(user)
    db.commit()

    return RedirectResponse("/user/login", status_code=302)


@router.get("/login")
def user_login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="user_login.html",
        context={}
    )


@router.post("/login")
def user_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(UserMaster).filter(
        UserMaster.email == email,
        UserMaster.status == "ACTIVE"
    ).first()

    if password != user.password:
        return templates.TemplateResponse(
            request=request,
            name="user_login.html",
            context={
                "error": "Invalid email or password"
            }
        )



    request.session["user_id"] = user.id
    request.session["user_email"] = user.email
    request.session["username"] = user.username
    request.session["role"] = "USER"

    return RedirectResponse("/products", status_code=302)


@router.get("/orders")
def user_orders(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("user_id"):
        return RedirectResponse("/user/login")

    orders = db.query(OrderMaster).filter(
        OrderMaster.user_id == request.session.get("user_id")
    ).order_by(OrderMaster.id.desc()).all()

    return templates.TemplateResponse(
        request=request,
        name="order_details.html",
        context={
            "orders": orders
        }
    )


@router.get("/logout")
def user_logout(request: Request):
    request.session.clear()
    return RedirectResponse("/user/login")