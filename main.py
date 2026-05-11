from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from database import engine
from models import Base

from routers import admin, user, item, cart, order

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="CHANGE_THIS_SECRET_KEY"
)

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