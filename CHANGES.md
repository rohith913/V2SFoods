# V2S Foods – Update Notes

## Changes Made

### 1. Dynamic Recipes (Admin CRUD)
- **New DB model**: `RecipeMaster` in `models.py` — stores slug, title, category, ingredients, steps, tips, nutrition, image, status.
- **New router**: `routers/recipe.py` — public routes (list, detail, like, comment) + admin CRUD (add, edit, delete).
- **New templates**:
  - `admin_recipes.html` — admin recipe listing with edit/delete/preview buttons.
  - `admin_recipe_form.html` — add/edit form with textarea inputs for ingredients, steps, tips, nutrition.
  - `recipes.html` — now dynamically renders DB recipes instead of hard-coded HTML.
- **Admin nav** — "Recipes" link added to admin navbar in `base.html`.
- Run `Base.metadata.create_all(bind=engine)` on app start to create the `recipe_master` table automatically.

### 2. Invoice Number + Print/Download
- **`OrderMaster`** now has `invoice_no` column (format: `INV-YYYY-NNNN`, e.g. `INV-2024-0001`).
- `routers/order.py` — `generate_invoice_no()` generates sequential invoice numbers per year.
- **New template**: `invoice.html` — professional printable invoice with Print button (browser print dialog) and Download PDF button (print-to-PDF).
- Invoice accessible at `/order/invoice/<order_id>` (users see own orders only, admins see all).
- **Invoice link** added to:
  - `order_success.html` — shown after placing an order.
  - `order_details.html` (user My Orders) — "Invoice / Print" button per order.
  - `all_orders.html` (admin All Orders) — "View Invoice" button per order.

### 3. Order Amount Mismatch Fix
- **Bug**: `routers/order.py` `/place` endpoint was calculating total as `price × qty` (ignoring `selected_kg`), while checkout showed `price × selected_kg × qty`.
- **Fix**: Both checkout and place-order now use `price × selected_kg × qty` consistently using `Decimal` arithmetic.
- Admin all-orders page now shows both "Items Total" (sum of `detail.amount`) and "Order Total" side by side for easy verification.

### 4. Redesigned Login Pages
- `admin_login.html` — split-screen layout: left decorative panel (features list) + right clean form with icon inputs.
- `user_login.html` — split-screen layout: left panel with trust badges + right form.
- Both use Poppins font, smooth focus animations, and gradient login button. Fully responsive (left panel hidden on mobile).
- **Existing CSS/design not changed** — login pages use their own scoped styles.

## Database Migration
The `recipe_master` and `invoice_no` column are new. Run your app once and SQLAlchemy will auto-create the `recipe_master` table. For `invoice_no` on an existing DB, run:
```sql
ALTER TABLE order_master ADD COLUMN IF NOT EXISTS invoice_no VARCHAR(100) UNIQUE;
```
