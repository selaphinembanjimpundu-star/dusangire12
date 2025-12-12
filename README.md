# Dusangire Hospital E-Commerce Restaurant

A Django-based e-commerce platform for a hospital restaurant providing healthy, medically-approved meals.

## Features

- User authentication and role-based access (Customer, Staff, Admin, Nutritionist)
- Menu management with categories and dietary tags
- Nutrition information tracking
- Responsive Bootstrap 5 UI

## Technology Stack

- **Backend**: Django 5.2.8
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Database**: SQLite (development) / PostgreSQL (production)

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

7. Access the application at `http://127.0.0.1:8000/`

## Project Structure

- `accounts/` - User authentication and profiles
- `menu/` - Menu items and categories
- `orders/` - Shopping cart and orders (Phase 3)
- `delivery/` - Delivery management (Phase 4)
- `payments/` - Payment processing (Phase 5)

## Development Phases

This project is being developed in phases. Currently completed:
- ✅ Phase 1: Foundation & Core Setup

See `PHASED_DEVELOPMENT_PLAN.md` for the complete development roadmap.

## Admin Panel

Access the admin panel at `/admin/` to manage:
- Users and profiles
- Menu categories
- Menu items
- Dietary tags

## License

All rights reserved.

