from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from database import engine
from models import Base
from routers import admin, user, item, cart, order

app = FastAPI(title="V2S Foods")

app.add_middleware(SessionMiddleware, secret_key="V2SFOODS_SECRET_KEY_2024")
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
Base.metadata.create_all(bind=engine)

app.include_router(admin.router)
app.include_router(user.router)
app.include_router(item.router)
app.include_router(cart.router)
app.include_router(order.router)


@app.get("/")
def home():
    return RedirectResponse("/products", status_code=302)


@app.get("/recipes")
def recipes_page(request: Request):
    return templates.TemplateResponse(request=request, name="recipes.html", context={
        "title": "Recipe Blog – V2S Foods"
    })


@app.get("/about")
def about_page(request: Request):
    return templates.TemplateResponse(request=request, name="about.html", context={
        "title": "About Us – V2S Foods"
    })


@app.get("/contact")
def contact_page(request: Request):
    return templates.TemplateResponse(request=request, name="contact.html", context={
        "title": "Contact Us – V2S Foods"
    })


@app.post("/contact")
async def contact_submit(request: Request):
    # In production, send email here
    return templates.TemplateResponse(request=request, name="contact.html", context={
        "title": "Contact Us – V2S Foods",
        "success": True
    })
