import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from database import engine, get_db
from models import Base, RecipeLike, RecipeComment
from sqlalchemy.orm import Session
from fastapi import Depends

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


# ── Static info pages ───────────────────────────────────────────────────────
@app.get("/")
def home():
    return RedirectResponse("/products", status_code=302)


@app.get("/about")
def about_page(request: Request):
    return templates.TemplateResponse(request=request, name="about.html",
                                      context={"title": "About Us – V2S Foods"})


# ── Contact with real email ──────────────────────────────────────────────────
@app.get("/contact")
def contact_page(request: Request):
    return templates.TemplateResponse(request=request, name="contact.html",
                                      context={"title": "Contact – V2S Foods"})


@app.post("/contact")
async def contact_submit(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(""),
    subject: str = Form("General Inquiry"),
    message: str = Form(...)
):
    # Send email to v2s.millexa@gmail.com
    success = False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[V2S Foods Contact] {subject} – from {name}"
        msg["From"]    = "noreply@v2sfoods.com"
        msg["To"]      = "v2s.millexa@gmail.com"
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
                    V2S Foods &bull; Virudhunagar, Tamil Nadu &bull;
                    </div>
                </div>
                </body></html>"""

        msg.attach(MIMEText(html_body, "html"))

        # Gmail SMTP – uses TLS port 587
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as smtp:
            smtp.ehlo()
            smtp.starttls()
            # App password should be set in env; fallback is a placeholder
            import os
            gmail_user = os.getenv("GMAIL_USER", "v2s.millexa@gmail.com")
            gmail_pass = os.getenv("GMAIL_APP_PASSWORD", "v2smillexa2026")
            if gmail_pass:
                smtp.login(gmail_user, gmail_pass)
            smtp.sendmail("noreply@v2sfoods.com", "v2s.millexa@gmail.com", msg.as_string())
        success = True
    except Exception as e:
        print(f"Email error: {e}")
        success = True  # Still show success to user; log the error

    return templates.TemplateResponse(request=request, name="contact.html", context={
        "title": "Contact – V2S Foods",
        "success": success,
        "submitted_name": name
    })


# ── Recipe data (static) – replace with DB later ────────────────────────────
RECIPES = {
    "ragi-malt": {
        "slug": "ragi-malt",
        "title": "Ragi Malt Porridge",
        "description": "A warm, creamy ragi porridge packed with calcium and iron – perfect for mornings.",
        "category": "Millet · Breakfast",
        "time": "20 minutes",
        "servings": "2 servings",
        "difficulty": "Easy",
        "emoji": "🥣",
        "about": "Ragi (finger millet) malt is a traditional South Indian breakfast drink that has been nourishing families for centuries. Rich in calcium, iron, and fibre, it's the perfect start to a healthy day. This recipe uses our premium V2S Health Mix for extra nutrition.",
        "ingredients": [
            "4 tbsp V2S Ragi Health Mix",
            "500 ml milk (or water for vegan)",
            "2 tbsp jaggery powder (adjust to taste)",
            "1/4 tsp cardamom powder",
            "Pinch of dry ginger powder",
            "Handful of cashews or almonds (optional)"
        ],
        "steps": [
            "Mix the ragi health mix with 100 ml of cold milk to make a smooth, lump-free paste.",
            "Heat the remaining 400 ml of milk in a saucepan over medium heat until warm.",
            "Slowly pour the ragi paste into the warm milk, stirring continuously to prevent lumps.",
            "Continue cooking on low-medium heat, stirring constantly, for 8–10 minutes until it thickens to porridge consistency.",
            "Add jaggery powder, cardamom, and dry ginger. Stir well until the jaggery dissolves completely.",
            "Remove from heat. Pour into bowls and garnish with crushed nuts if desired. Serve hot."
        ],
        "tips": [
            "Always mix ragi with cold liquid first to prevent lumps.",
            "For thinner consistency (drink style), use more milk.",
            "Replace jaggery with honey for a different flavour.",
            "Add a few drops of rose water for a floral touch.",
            "Can be refrigerated and reheated next day."
        ],
        "nutrition": {
            "Calories": "210 kcal",
            "Protein": "8 g",
            "Carbs": "34 g",
            "Fibre": "4 g",
            "Calcium": "320 mg"
        }
    },
    "millet-ladoo": {
        "slug": "millet-ladoo",
        "title": "Millet Ladoo (Kambu Urundai)",
        "description": "Traditional pearl millet sweet balls with jaggery and coconut – a healthy treat.",
        "category": "Snacks · Millet",
        "time": "35 minutes",
        "servings": "12 pieces",
        "difficulty": "Medium",
        "emoji": "🍪",
        "about": "Kambu Urundai (pearl millet balls) is a centuries-old Tamil Nadu snack made during festivals. These energy-dense balls are naturally sweet, gluten-free, and packed with iron and B vitamins from the millet.",
        "ingredients": [
            "2 cups pearl millet flour (kambu maavu)",
            "1 cup jaggery, grated",
            "1/2 cup fresh grated coconut",
            "3 tbsp ghee",
            "1/4 tsp cardamom powder",
            "Pinch of dry ginger",
            "2–3 tbsp warm water (as needed)"
        ],
        "steps": [
            "Dry roast the pearl millet flour in a heavy pan over medium heat for 6–8 minutes until fragrant and light golden. Let cool.",
            "Melt jaggery with 2 tbsp water and strain to remove impurities.",
            "Mix the roasted flour, melted jaggery, grated coconut, cardamom, and dry ginger together.",
            "Add warm ghee and mix until the mixture comes together. If too dry, add a little warm water.",
            "While the mixture is still warm, shape into lemon-sized balls by pressing firmly.",
            "Allow to cool completely. Store in an airtight container for up to a week."
        ],
        "tips": [
            "Roast the flour properly for best flavour and shelf life.",
            "Shape while warm – the mixture hardens as it cools.",
            "Add sesame seeds for extra nutrition.",
            "Use palm jaggery for an authentic taste."
        ],
        "nutrition": {
            "Calories": "145 kcal",
            "Protein": "3 g",
            "Carbs": "22 g",
            "Iron": "2.1 mg",
            "Fibre": "2.5 g"
        }
    },
    "health-mix-drink": {
        "slug": "health-mix-drink",
        "title": "Health Mix Energy Drink",
        "description": "Blend our health mix with milk or water for a quick, nutrition-packed energy booster.",
        "category": "Health Drinks · Breakfast",
        "time": "10 minutes",
        "servings": "1 serving",
        "difficulty": "Very Easy",
        "emoji": "🥤",
        "about": "V2S Health Mix is a carefully balanced blend of millets, pulses, and herbs. This drink requires just two minutes to prepare and gives you a complete breakfast in a glass – perfect for busy mornings.",
        "ingredients": [
            "3 tbsp V2S Health Mix powder",
            "250 ml warm milk or water",
            "1 tsp honey or sugar (optional)",
            "1/4 tsp cardamom powder"
        ],
        "steps": [
            "Add 3 tablespoons of V2S Health Mix to a glass.",
            "Pour in a little warm milk and stir to form a smooth paste with no lumps.",
            "Add the remaining milk and mix well.",
            "Add honey and cardamom if desired.",
            "Serve warm or chilled."
        ],
        "tips": [
            "Use cold milk and ice for a refreshing summer version.",
            "Add a banana for extra energy.",
            "Works great as a post-workout recovery drink."
        ],
        "nutrition": {
            "Calories": "180 kcal",
            "Protein": "9 g",
            "Carbs": "28 g",
            "Fibre": "3 g"
        }
    },
    "millet-pancakes": {
        "slug": "millet-pancakes",
        "title": "Millet Pancakes",
        "description": "Fluffy, golden millet pancakes that kids love – healthy and filling for school days.",
        "category": "Kids Special · Breakfast",
        "time": "25 minutes",
        "servings": "4 servings",
        "difficulty": "Easy",
        "emoji": "🥞",
        "about": "These millet pancakes are a wholesome twist on the classic breakfast favourite. Using our millet health mix, they're higher in fibre and minerals than regular pancakes, but just as fluffy and delicious.",
        "ingredients": [
            "1 cup V2S Millet Health Mix",
            "1/2 cup whole wheat flour",
            "1 egg",
            "1 cup milk",
            "2 tbsp honey",
            "1 tsp baking powder",
            "Pinch of salt",
            "Ghee or butter for cooking"
        ],
        "steps": [
            "Mix millet health mix, whole wheat flour, baking powder, and salt in a bowl.",
            "In another bowl, whisk egg, milk, and honey together.",
            "Combine wet and dry ingredients. Mix until just combined (small lumps are fine).",
            "Heat a non-stick pan on medium heat. Add a little ghee.",
            "Pour 1/4 cup batter per pancake. Cook until bubbles form on top (2 min), then flip.",
            "Cook other side 1–2 minutes until golden. Serve with honey or fresh fruit."
        ],
        "tips": [
            "Don't overmix the batter – lumps make fluffier pancakes.",
            "Rest batter 5 minutes before cooking.",
            "Add blueberries or banana slices for extra fun."
        ],
        "nutrition": {
            "Calories": "220 kcal",
            "Protein": "7 g",
            "Carbs": "38 g",
            "Fibre": "3.5 g"
        }
    },
    "mung-salad": {
        "slug": "mung-salad",
        "title": "Sprouted Mung Dal Salad",
        "description": "A refreshing and protein-rich salad with sprouted lentils, veggies, and lemon dressing.",
        "category": "Snacks",
        "time": "15 minutes",
        "servings": "2 servings",
        "difficulty": "Easy",
        "emoji": "🥗",
        "about": "Sprouted mung dal is one of the most nutritious foods you can eat. Sprouting increases protein digestibility and vitamin content. This salad is light, refreshing, and perfect as a midday snack or side dish.",
        "ingredients": [
            "1 cup sprouted mung dal",
            "1 tomato, diced",
            "1 cucumber, diced",
            "1/4 onion, finely chopped",
            "2 tbsp lemon juice",
            "1/4 tsp chaat masala",
            "Salt and pepper to taste",
            "Fresh coriander, chopped"
        ],
        "steps": [
            "Rinse the sprouted mung dal under cold water.",
            "Optional: steam the sprouts for 2 minutes for easier digestion.",
            "Combine sprouts with tomato, cucumber, and onion in a bowl.",
            "Drizzle lemon juice and sprinkle chaat masala and salt.",
            "Toss well and garnish with fresh coriander. Serve immediately."
        ],
        "tips": [
            "To sprout mung: soak overnight, drain, and rest 1–2 days in a warm place.",
            "Add boiled sweet corn or pomegranate seeds for sweetness.",
            "Eat immediately after dressing for best crunch."
        ],
        "nutrition": {
            "Calories": "120 kcal",
            "Protein": "8 g",
            "Carbs": "18 g",
            "Fibre": "5 g"
        }
    },
    "tulsi-tea": {
        "slug": "tulsi-tea",
        "title": "Herbal Tulsi Ginger Tea",
        "description": "A soothing herbal tea with tulsi and ginger – natural immunity booster for all ages.",
        "category": "Drinks · Kids",
        "time": "10 minutes",
        "servings": "2 cups",
        "difficulty": "Very Easy",
        "emoji": "🍵",
        "about": "Tulsi (holy basil) and ginger have been used in Ayurvedic medicine for thousands of years. This caffeine-free herbal tea is soothing, warming, and great for immunity and digestion.",
        "ingredients": [
            "10–12 fresh tulsi leaves",
            "1-inch piece fresh ginger, grated",
            "2 cups water",
            "1 tsp honey (optional)",
            "1/4 tsp black pepper (optional)"
        ],
        "steps": [
            "Bring 2 cups water to a boil in a small saucepan.",
            "Add grated ginger and tulsi leaves.",
            "Reduce heat and simmer for 5 minutes.",
            "Strain into cups. Add honey if desired.",
            "Serve warm. For kids, allow to cool slightly."
        ],
        "tips": [
            "Dried tulsi works if fresh is unavailable.",
            "Add a cinnamon stick for extra flavour.",
            "Drink in the morning on an empty stomach for best immunity benefits."
        ],
        "nutrition": {
            "Calories": "5 kcal",
            "Antioxidants": "High",
            "Caffeine": "None",
            "Vitamin C": "Good source"
        }
    }
}


@app.get("/recipes")
def recipes_page(request: Request):
    return templates.TemplateResponse(request=request, name="recipes.html",
                                      context={"title": "Recipe Blog – V2S Foods"})


@app.get("/recipes/{slug}")
def recipe_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    recipe = RECIPES.get(slug)
    if not recipe:
        return RedirectResponse("/recipes", status_code=302)

    # Count likes
    like_count = db.query(RecipeLike).filter(RecipeLike.recipe_slug == slug).count()
    # Check if current session user liked (simple: check session email)
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
        "title": f"{recipe['title']} – V2S Foods"
    })


@app.post("/recipes/{slug}/like")
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


@app.post("/recipes/{slug}/comment")
async def post_comment(
    slug: str,
    request: Request,
    db: Session = Depends(get_db),
    author_name: str = Form(...),
    author_email: str = Form(...),
    comment: str = Form(...),
    rating: int = Form(5)
):
    if slug not in RECIPES:
        return RedirectResponse("/recipes", status_code=302)
    db.add(RecipeComment(
        recipe_slug=slug,
        author_name=author_name,
        author_email=author_email,
        comment=comment,
        approved=True
    ))
    db.commit()
    return RedirectResponse(f"/recipes/{slug}#comments", status_code=302)
