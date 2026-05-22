import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from database import engine, get_db
from models import Base
from sqlalchemy.orm import Session
from fastapi import Depends

from routers import admin, user, item, cart, order
from routers import recipe as recipe_router

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
app.include_router(recipe_router.router)


@app.get("/")
def home():
    return RedirectResponse("/products", status_code=302)


@app.get("/about")
def about_page(request: Request):
    return templates.TemplateResponse(request=request, name="about.html",
                                      context={"title": "About Us – V2S Foods"})


@app.get("/contact")
def contact_page(request: Request):
    return templates.TemplateResponse(request=request, name="contact.html",
                                      context={"title": "Contact – V2S Foods"})


@app.post("/contact")
async def contact_submit(
    request: Request,
    name: str = Form(...), email: str = Form(...),
    phone: str = Form(""), subject: str = Form("General Inquiry"),
    message: str = Form(...)
):
    success = False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[V2S Foods Contact] {subject} – from {name}"
        msg["From"] = "noreply@v2sfoods.com"
        msg["To"] = "v2s.millexa@gmail.com"
        msg["Reply-To"] = email

        html_body = f"""
            <html><body style="font-family:Arial,sans-serif;color:#333;">
            <div style="max-width:600px;margin:auto;border:1px solid #ddd;border-radius:12px;overflow:hidden;">
                <div style="background:#3f4f24;padding:20px;text-align:center;">
                <h2 style="color:#c8d993;margin:0;">V2S Foods – New Message</h2>
                </div>
                <div style="padding:28px;">
                <table style="width:100%;border-collapse:collapse;">
                    <tr><td style="padding:8px 0;color:#666;width:120px;"><strong>Name</strong></td><td style="padding:8px 0;">{name}</td></tr>
                    <tr><td style="padding:8px 0;color:#666;"><strong>Email</strong></td><td style="padding:8px 0;"><a href="mailto:{email}">{email}</a></td></tr>
                    <tr><td style="padding:8px 0;color:#666;"><strong>Phone</strong></td><td style="padding:8px 0;">{phone or '—'}</td></tr>
                    <tr><td style="padding:8px 0;color:#666;"><strong>Subject</strong></td><td style="padding:8px 0;">{subject}</td></tr>
                </table>
                <hr style="border:none;border-top:1px solid #eee;margin:16px 0;">
                <h3 style="color:#3f4f24;margin:0 0 10px;">Message</h3>
                <p style="background:#f7faef;padding:16px;border-radius:8px;line-height:1.7;">{message}</p>
                </div>
                <div style="background:#f0f0f0;padding:14px;text-align:center;font-size:12px;color:#999;">
                V2S Foods &bull; Virudhunagar, Tamil Nadu
                </div>
            </div>
            </body></html>"""

        msg.attach(MIMEText(html_body, "html"))
        import os
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as smtp:
            smtp.ehlo()
            smtp.starttls()
            gmail_user = os.getenv("GMAIL_USER", "v2s.millexa@gmail.com")
            gmail_pass = os.getenv("GMAIL_APP_PASSWORD", "v2smillexa2026")
            if gmail_pass:
                smtp.login(gmail_user, gmail_pass)
            smtp.sendmail("noreply@v2sfoods.com", "v2s.millexa@gmail.com", msg.as_string())
        success = True
    except Exception as e:
        print(f"Email error: {e}")
        success = True

    return templates.TemplateResponse(request=request, name="contact.html", context={
        "title": "Contact – V2S Foods", "success": success, "submitted_name": name
    })
