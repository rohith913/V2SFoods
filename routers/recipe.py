"""
Dynamic Recipe router – admin CRUD + public listing/detail
"""
import json
import os
import re
import shutil
from uuid import uuid4

from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
from models import RecipeMaster, RecipeLike, RecipeComment

router = APIRouter(tags=["Recipe"])
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "static/uploads/recipes"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ── helpers ──────────────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s_-]+", "-", text)


def save_image(file: UploadFile | None) -> str:
    if not file or not file.filename:
        return ""
    ext = os.path.splitext(file.filename)[1]
    fname = f"{uuid4().hex}{ext}"
    with open(os.path.join(UPLOAD_DIR, fname), "wb") as buf:
        shutil.copyfileobj(file.file, buf)
    return f"/static/uploads/recipes/{fname}"


def lines_to_list(text: str) -> list:
    """Convert newline-separated textarea input to a list."""
    return [l.strip() for l in text.splitlines() if l.strip()]


def pairs_to_dict(text: str) -> dict:
    """Convert 'Key: Value' lines to a dict for nutrition."""
    result = {}
    for line in text.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            if k.strip():
                result[k.strip()] = v.strip()
    return result


# ── Public routes ─────────────────────────────────────────────────────────────

@router.get("/recipes")
def recipes_page(request: Request, db: Session = Depends(get_db)):
    recipes = db.query(RecipeMaster).filter(
        RecipeMaster.status == "ACTIVE"
    ).order_by(RecipeMaster.id.desc()).all()
    return templates.TemplateResponse(request=request, name="recipes.html",
                                      context={"title": "Recipe Blog – V2S Foods",
                                               "recipes": recipes})


@router.get("/recipes/{slug}")
def recipe_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    recipe = db.query(RecipeMaster).filter(RecipeMaster.slug == slug).first()
    if not recipe:
        return RedirectResponse("/recipes", status_code=302)

    # parse JSON fields
    recipe.ingredients = json.loads(recipe.ingredients_json or "[]")
    recipe.steps = json.loads(recipe.steps_json or "[]")
    recipe.tips = json.loads(recipe.tips_json or "[]")
    recipe.nutrition = json.loads(recipe.nutrition_json or "{}")

    like_count = db.query(RecipeLike).filter(RecipeLike.recipe_slug == slug).count()
    user_email = request.session.get("user_email", "")
    liked = False
    if user_email:
        liked = db.query(RecipeLike).filter(
            RecipeLike.recipe_slug == slug,
            RecipeLike.user_email == user_email
        ).first() is not None

    comments = db.query(RecipeComment).filter(
        RecipeComment.recipe_slug == slug,
        RecipeComment.approved == True
    ).order_by(RecipeComment.id.desc()).all()

    return templates.TemplateResponse(request=request, name="recipe_detail.html", context={
        "recipe": recipe,
        "like_count": like_count,
        "liked": liked,
        "comments": comments,
        "title": f"{recipe.title} – V2S Foods"
    })


@router.post("/recipes/{slug}/like")
def like_recipe(slug: str, request: Request, db: Session = Depends(get_db)):
    user_email = request.session.get("user_email", request.client.host)
    existing = db.query(RecipeLike).filter(
        RecipeLike.recipe_slug == slug,
        RecipeLike.user_email == user_email
    ).first()
    if existing:
        db.delete(existing)
        db.commit()
        liked = False
    else:
        db.add(RecipeLike(recipe_slug=slug, user_email=user_email))
        db.commit()
        liked = True
    count = db.query(RecipeLike).filter(RecipeLike.recipe_slug == slug).count()
    return JSONResponse({"liked": liked, "count": count})


@router.post("/recipes/{slug}/comment")
async def post_comment(
    slug: str, request: Request, db: Session = Depends(get_db),
    author_name: str = Form(...), author_email: str = Form(...),
    comment: str = Form(...), rating: int = Form(5)
):
    recipe = db.query(RecipeMaster).filter(RecipeMaster.slug == slug).first()
    if not recipe:
        return RedirectResponse("/recipes", status_code=302)
    db.add(RecipeComment(recipe_slug=slug, author_name=author_name,
                         author_email=author_email, comment=comment, approved=True))
    db.commit()
    return RedirectResponse(f"/recipes/{slug}#comments", status_code=302)


# ── Admin routes ──────────────────────────────────────────────────────────────

@router.get("/admin/recipes")
def admin_recipes(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("admin_id"):
        return RedirectResponse("/admin/login")
    recipes = db.query(RecipeMaster).order_by(RecipeMaster.id.desc()).all()
    return templates.TemplateResponse(request=request, name="admin_recipes.html",
                                      context={"recipes": recipes, "title": "Manage Recipes"})


@router.get("/admin/recipes/add")
def admin_recipe_add_page(request: Request):
    if not request.session.get("admin_id"):
        return RedirectResponse("/admin/login")
    return templates.TemplateResponse(request=request, name="admin_recipe_form.html",
                                      context={"recipe": None, "title": "Add Recipe"})


@router.post("/admin/recipes/add")
async def admin_recipe_add(
    request: Request, db: Session = Depends(get_db),
    title: str = Form(...),
    description: str = Form(""),
    category: str = Form(""),
    time_minutes: str = Form(""),
    servings: str = Form(""),
    difficulty: str = Form("Easy"),
    emoji: str = Form("🍲"),
    about: str = Form(""),
    ingredients_text: str = Form(""),
    steps_text: str = Form(""),
    tips_text: str = Form(""),
    nutrition_text: str = Form(""),
    status: str = Form("ACTIVE"),
    image_file: UploadFile = File(None),
):
    if not request.session.get("admin_id"):
        return RedirectResponse("/admin/login")

    slug = slugify(title)
    # ensure unique slug
    existing = db.query(RecipeMaster).filter(RecipeMaster.slug == slug).first()
    if existing:
        slug = slug + "-" + uuid4().hex[:4]

    image_url = save_image(image_file)

    recipe = RecipeMaster(
        slug=slug, title=title, description=description, category=category,
        time_minutes=time_minutes, servings=servings, difficulty=difficulty,
        emoji=emoji, about=about,
        ingredients_json=json.dumps(lines_to_list(ingredients_text)),
        steps_json=json.dumps(lines_to_list(steps_text)),
        tips_json=json.dumps(lines_to_list(tips_text)),
        nutrition_json=json.dumps(pairs_to_dict(nutrition_text)),
        image_url=image_url, status=status
    )
    db.add(recipe)
    db.commit()
    return RedirectResponse("/admin/recipes", status_code=302)


@router.get("/admin/recipes/edit/{recipe_id}")
def admin_recipe_edit_page(recipe_id: int, request: Request, db: Session = Depends(get_db)):
    if not request.session.get("admin_id"):
        return RedirectResponse("/admin/login")
    recipe = db.query(RecipeMaster).filter(RecipeMaster.id == recipe_id).first()
    if not recipe:
        return RedirectResponse("/admin/recipes")

    # expand JSON for textarea
    recipe.ingredients_text = "\n".join(json.loads(recipe.ingredients_json or "[]"))
    recipe.steps_text = "\n".join(json.loads(recipe.steps_json or "[]"))
    recipe.tips_text = "\n".join(json.loads(recipe.tips_json or "[]"))
    nutrition = json.loads(recipe.nutrition_json or "{}")
    recipe.nutrition_text = "\n".join(f"{k}: {v}" for k, v in nutrition.items())

    return templates.TemplateResponse(request=request, name="admin_recipe_form.html",
                                      context={"recipe": recipe, "title": "Edit Recipe"})


@router.post("/admin/recipes/edit/{recipe_id}")
async def admin_recipe_edit(
    recipe_id: int, request: Request, db: Session = Depends(get_db),
    title: str = Form(...),
    description: str = Form(""),
    category: str = Form(""),
    time_minutes: str = Form(""),
    servings: str = Form(""),
    difficulty: str = Form("Easy"),
    emoji: str = Form("🍲"),
    about: str = Form(""),
    ingredients_text: str = Form(""),
    steps_text: str = Form(""),
    tips_text: str = Form(""),
    nutrition_text: str = Form(""),
    status: str = Form("ACTIVE"),
    image_file: UploadFile = File(None),
):
    if not request.session.get("admin_id"):
        return RedirectResponse("/admin/login")

    recipe = db.query(RecipeMaster).filter(RecipeMaster.id == recipe_id).first()
    if not recipe:
        return RedirectResponse("/admin/recipes")

    recipe.title = title
    recipe.description = description
    recipe.category = category
    recipe.time_minutes = time_minutes
    recipe.servings = servings
    recipe.difficulty = difficulty
    recipe.emoji = emoji
    recipe.about = about
    recipe.ingredients_json = json.dumps(lines_to_list(ingredients_text))
    recipe.steps_json = json.dumps(lines_to_list(steps_text))
    recipe.tips_json = json.dumps(lines_to_list(tips_text))
    recipe.nutrition_json = json.dumps(pairs_to_dict(nutrition_text))
    recipe.status = status

    if image_file and image_file.filename:
        recipe.image_url = save_image(image_file)

    db.commit()
    return RedirectResponse("/admin/recipes", status_code=302)


@router.post("/admin/recipes/delete/{recipe_id}")
def admin_recipe_delete(recipe_id: int, request: Request, db: Session = Depends(get_db)):
    if not request.session.get("admin_id"):
        return RedirectResponse("/admin/login")
    recipe = db.query(RecipeMaster).filter(RecipeMaster.id == recipe_id).first()
    if recipe:
        db.delete(recipe)
        db.commit()
    return RedirectResponse("/admin/recipes", status_code=302)
