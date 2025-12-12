# Phase 1 Setup Guide

## ✅ Phase 1 Complete!

All Phase 1 tasks have been completed:

1. ✅ Django project structure initialized
2. ✅ Apps created (accounts, menu, orders, delivery, payments)
3. ✅ Database models created (User, Profile, Category, MenuItem, DietaryTag)
4. ✅ User authentication implemented (login, register, logout)
5. ✅ User roles system (Customer, Staff, Admin, Nutritionist)
6. ✅ Base templates with Bootstrap 5
7. ✅ Login and Register pages
8. ✅ Menu listing and detail pages
9. ✅ Static files configured
10. ✅ Admin panel configured

## Quick Start

1. **Create a superuser** (if you haven't already):
   ```bash
   python manage.py createsuperuser
   ```

2. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

3. **Access the application**:
   - Homepage: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/
   - Menu: http://127.0.0.1:8000/menu/
   - Login: http://127.0.0.1:8000/accounts/login/
   - Register: http://127.0.0.1:8000/accounts/register/

## Adding Sample Data

1. **Login to Admin Panel** at `/admin/`

2. **Create Categories**:
   - Go to Menu > Categories
   - Add categories like: Breakfast, Lunch, Dinner, Snacks, Beverages

3. **Create Dietary Tags**:
   - Go to Menu > Dietary Tags
   - Add tags like: Diabetic, Low-Sodium, High-Protein, Post-Surgery, Vegetarian

4. **Create Menu Items**:
   - Go to Menu > Menu Items
   - Add items with:
     - Name, Description, Category
     - Price
     - Dietary Tags (optional)
     - Nutrition Information (optional)
     - Image (optional)

5. **Create Users**:
   - Users can register themselves at `/accounts/register/`
   - Or create them in the admin panel
   - Assign roles (Customer, Staff, Admin, Nutritionist) via Profile

## Testing the Application

1. **Register a new user**:
   - Go to `/accounts/register/`
   - Fill in the form
   - Select account type (Customer, Staff, Admin, or Nutritionist)
   - Submit

2. **Login**:
   - Go to `/accounts/login/`
   - Use your credentials

3. **View Menu**:
   - Navigate to `/menu/` or click "Menu" in navbar
   - Browse items by category
   - Click "View Details" to see item details

4. **Update Profile**:
   - Login and click your username in navbar
   - Select "Profile"
   - Update your information

## Project Structure

```
dusangire/
├── accounts/          # User authentication & profiles
├── menu/              # Menu items & categories
├── orders/            # Shopping cart & orders (Phase 3)
├── delivery/          # Delivery management (Phase 4)
├── payments/          # Payment processing (Phase 5)
├── dusangire/         # Main project settings
├── templates/         # HTML templates
├── static/            # CSS, JS, images
└── media/             # User uploaded files
```

## Next Steps - Phase 2

Phase 2 will focus on:
- Enhanced menu filtering and search
- Menu item image uploads
- Better menu display with filters
- Category management improvements

See `PHASED_DEVELOPMENT_PLAN.md` for the complete roadmap.

## Notes

- The SECRET_KEY warning in settings.py is normal for development
- For production, move SECRET_KEY to environment variables
- Static files are served automatically in development mode
- Media files (menu images) will be stored in the `media/` directory

