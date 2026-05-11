import os
import shutil
from uuid import uuid4

from fastapi import APIRouter, Request, Form, Depends, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
from models import ItemMaster

router = APIRouter(tags=["Item"])

templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "static/uploads/items"
MAX_VIDEO_SIZE = 10 * 1024 * 1024  # 10 MB

os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_upload_file(file: UploadFile | None, allowed_types=None):
    if not file or not file.filename:
        return ""

    if allowed_types:
        content_type = file.content_type or ""
        if not any(content_type.startswith(t) for t in allowed_types):
            raise ValueError("Invalid file type")

    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return f"/static/uploads/items/{filename}"


def save_video_file(file: UploadFile | None):
    if not file or not file.filename:
        return ""

    content_type = file.content_type or ""

    if not content_type.startswith("video/"):
        raise ValueError("Only video files allowed")

    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)

    if size > MAX_VIDEO_SIZE:
        raise ValueError("Video size should not exceed 10 MB")

    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return f"/static/uploads/items/{filename}"


@router.get("/admin/item-master")
def item_master_page(
    request: Request,
    search_item: str = "",
    db: Session = Depends(get_db)
):
    if not request.session.get("admin_id"):
        return RedirectResponse("/admin/login")

    query = db.query(ItemMaster)

    if search_item:
        query = query.filter(ItemMaster.item_name.ilike(f"%{search_item}%"))

    items = query.order_by(ItemMaster.id.desc()).all()

    return templates.TemplateResponse(
        request=request,
        name="item_master.html",
        context={
            "items": items,
            "search_item": search_item
        }
    )


@router.post("/admin/item-master")
def add_item(
    request: Request,

    item_code: str = Form(...),
    item_name: str = Form(...),
    description: str = Form(""),
    category: str = Form(""),

    ingredients: str = Form(""),
    how_to_use: str = Form(""),
    specifications: str = Form(""),

    price: float = Form(...),
    stock_qty: int = Form(...),
    status: str = Form("ACTIVE"),

    main_image: UploadFile = File(None),
    image_1: UploadFile = File(None),
    image_2: UploadFile = File(None),
    image_3: UploadFile = File(None),
    image_4: UploadFile = File(None),
    image_5: UploadFile = File(None),
    video_file: UploadFile = File(None),

    db: Session = Depends(get_db)
):
    if not request.session.get("admin_id"):
        return RedirectResponse("/admin/login")

    existing = db.query(ItemMaster).filter(
        ItemMaster.item_code == item_code
    ).first()

    if existing:
        items = db.query(ItemMaster).order_by(ItemMaster.id.desc()).all()

        return templates.TemplateResponse(
            request=request,
            name="item_master.html",
            context={
                "items": items,
                "search_item": "",
                "error": "Item code already exists"
            }
        )

    try:
        main_image_path = save_upload_file(main_image, allowed_types=["image/"])
        image_1_path = save_upload_file(image_1, allowed_types=["image/"])
        image_2_path = save_upload_file(image_2, allowed_types=["image/"])
        image_3_path = save_upload_file(image_3, allowed_types=["image/"])
        image_4_path = save_upload_file(image_4, allowed_types=["image/"])
        image_5_path = save_upload_file(image_5, allowed_types=["image/"])
        video_path = save_video_file(video_file)

    except ValueError as e:
        items = db.query(ItemMaster).order_by(ItemMaster.id.desc()).all()

        return templates.TemplateResponse(
            request=request,
            name="item_master.html",
            context={
                "items": items,
                "search_item": "",
                "error": str(e)
            }
        )

    item = ItemMaster(
        item_code=item_code,
        item_name=item_name,
        description=description,
        category=category,

        ingredients=ingredients,
        how_to_use=how_to_use,
        specifications=specifications,

        price=price,
        stock_qty=stock_qty,

        main_image=main_image_path,
        image_1=image_1_path,
        image_2=image_2_path,
        image_3=image_3_path,
        image_4=image_4_path,
        image_5=image_5_path,
        video_url=video_path,

        status=status
    )

    db.add(item)
    db.commit()

    return RedirectResponse("/admin/item-master", status_code=302)


@router.get("/admin/item-list")
def admin_item_list_redirect():
    return RedirectResponse("/admin/item-master")


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