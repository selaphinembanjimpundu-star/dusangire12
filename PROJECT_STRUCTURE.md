# Dusangire Project Structure Guide

## Recommended Django Project Structure

```
dusangire_project/
│
├── dusangire/                    # Main project directory
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py              # Base settings
│   │   ├── development.py        # Development settings
│   │   └── production.py         # Production settings
│   ├── urls.py                   # Main URL configuration
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                     # User authentication & profiles
│   ├── __init__.py
│   ├── models.py                 # User, Profile models
│   ├── views.py                  # Auth views
│   ├── forms.py                  # Registration, login forms
│   ├── urls.py
│   ├── admin.py
│   └── templates/accounts/
│       ├── login.html
│       ├── register.html
│       └── profile.html
│
├── menu/                         # Menu management
│   ├── __init__.py
│   ├── models.py                 # Category, MenuItem, DietaryTag
│   ├── views.py                  # Menu views
│   ├── forms.py                  # Menu forms
│   ├── urls.py
│   ├── admin.py
│   └── templates/menu/
│       ├── menu_list.html
│       ├── menu_detail.html
│       └── menu_filter.html
│
├── orders/                       # Cart & orders
│   ├── __init__.py
│   ├── models.py                 # Cart, Order, OrderItem
│   ├── views.py                  # Cart & order views
│   ├── forms.py                  # Order forms
│   ├── urls.py
│   ├── admin.py
│   └── templates/orders/
│       ├── cart.html
│       ├── checkout.html
│       └── order_history.html
│
├── delivery/                     # Delivery management
│   ├── __init__.py
│   ├── models.py                 # DeliveryAddress, DeliveryZone
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
│
├── payments/                     # Payment processing
│   ├── __init__.py
│   ├── models.py                 # Payment, PaymentMethod
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
│
├── static/                       # Static files
│   ├── css/
│   │   ├── style.css
│   │   └── custom.css
│   ├── js/
│   │   ├── main.js
│   │   ├── cart.js
│   │   └── menu.js
│   ├── images/
│   │   └── menu_items/
│   └── bootstrap/                # Bootstrap files (or use CDN)
│
├── media/                        # User uploaded files
│   └── menu_images/
│
├── templates/                     # Base templates
│   ├── base.html
│   ├── navbar.html
│   ├── footer.html
│   └── includes/
│       ├── messages.html
│       └── cart_icon.html
│
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (gitignored)
├── .gitignore
├── manage.py
└── README.md
```

## Initial Setup Commands

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install Django
pip install django

# Create project
django-admin startproject dusangire .

# Create apps
python manage.py startapp accounts
python manage.py startapp menu
python manage.py startapp orders
python manage.py startapp delivery
python manage.py startapp payments

# Install additional packages
pip install django-crispy-forms crispy-bootstrap5
pip install Pillow
pip install django-environ
pip install python-decouple

# Create requirements.txt
pip freeze > requirements.txt
```

## Base Template Structure (Bootstrap 5)

### templates/base.html

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{% block title %}Dusangire Restaurant{% endblock %}</title>

    <!-- Bootstrap 5 CSS -->
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
      rel="stylesheet"
    />

    <!-- Custom CSS -->
    {% load static %}
    <link rel="stylesheet" href="{% static 'css/style.css' %}" />

    {% block extra_css %}{% endblock %}
  </head>
  <body>
    {% include 'navbar.html' %}

    <main>
      {% if messages %} {% include 'includes/messages.html' %} {% endif %} {%
      block content %}{% endblock %}
    </main>

    {% include 'footer.html' %}

    <!-- Bootstrap 5 JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

    <!-- Custom JS -->
    <script src="{% static 'js/main.js' %}"></script>

    {% block extra_js %}{% endblock %}
  </body>
</html>
```

## Key Settings Configuration

### settings/base.py (excerpt)

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party
    'crispy_forms',
    'crispy_bootstrap5',

    # Local apps
    'accounts',
    'menu',
    'orders',
    'delivery',
    'payments',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

## Database Models Quick Reference

### accounts/models.py (Phase 1)

- User (extends Django User)
- Profile (phone, address, dietary_preferences)

### menu/models.py (Phase 2)

- Category
- DietaryTag
- MenuItem (with image, price, category, tags)
- NutritionInfo

### orders/models.py (Phase 3)

- Cart
- CartItem
- Order
- OrderItem
- OrderStatus

### delivery/models.py (Phase 4)

- DeliveryAddress
- DeliveryZone

### payments/models.py (Phase 5)

- PaymentMethod
- Payment

## Next Steps

1. Follow Phase 1 from PHASED_DEVELOPMENT_PLAN.md
2. Set up the project structure above
3. Initialize Git repository
4. Create initial database migrations
5. Build base templates with Bootstrap
