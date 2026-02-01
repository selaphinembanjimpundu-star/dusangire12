# Dusangire Hospital E-Commerce Restaurant

A comprehensive Django-based health management and meal planning platform with role-based access control, health check auto-assignment, and integrated consultation system.

## Features

- **User Authentication**: Django-Allauth with social OAuth and local registration
- **Role-Based Access Control (RBAC)**: 10 user roles with 45+ granular permissions
- **Health Check Auto-Assignment**: Automatic real-time assignment to available consultants
- **Menu Management**: Categories, dietary tags, nutrition information
- **Order Management**: Multi-role ordering and tracking
- **Subscriptions**: Flexible subscription models
- **Payments**: Integrated payment gateway
- **Consultations**: Nutritionist and medical staff consultations
- **Analytics**: Business and health insights
- **Review System**: Patient feedback and ratings
- **Support Ticketing**: Customer support system
- **Responsive UI**: Bootstrap 5 responsive design

## Technology Stack

- **Backend**: Django 5.2.8
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: Django-Allauth
- **API**: Django REST Framework
- **Deployment**: Gunicorn + Docker ready

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/dusangire.git
   cd dusangire
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # macOS/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

8. Access the application at `http://127.0.0.1:8000/`

## Project Structure

- `accounts/` - User authentication, profiles, and roles
- `health_profiles/` - **NEW** Health checks with auto-assignment system
- `menu/` - Menu items and categories
- `orders/` - Shopping cart and order management
- `delivery/` - Delivery tracking
- `payments/` - Payment processing
- `subscriptions/` - Subscription management
- `nutritionist_dashboard/` - Nutritionist interface
- `customer_dashboard/` - Customer portal
- `admin_dashboard/` - Administrative interface
- `analytics/` - Analytics and reporting
- `reviews/` - Review and rating system
- `support/` - Support ticketing
- `loyalty/` - Loyalty program
- `catering/` - Catering services
- `notifications/` - Notification system

## Key Features

### Health Check Auto-Assignment (NEW)

Automatically assigns health checks to available consultants with:
- Real-time signal processing
- Workload management
- Priority handling
- Batch assignment command
- Complete audit logging
- Email notifications

Access at: `/health-checks/`

### Admin Panel

Access the admin panel at `/admin/` to manage:
- Users, profiles, and roles
- Menu categories and items
- Dietary tags
- Orders and deliveries
- **Health Checks** - Create, filter, and manage checks
- **Consultant Availability** - Monitor workload and performance
- **Assignment Logs** - View all assignment attempts

## Development Phases

This project has been developed in multiple phases:
- ✅ Phase 1-4: Foundation, Core Setup, Multi-role System, Analytics
- ✅ Phase 5: Health Check Auto-Assignment System (NEW)
- 🔄 Phase 6+: Planned enhancements

See individual `PHASE*.md` files for detailed documentation.

## Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test health_profiles

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## Deployment

For detailed deployment instructions, see [GITHUB_DEPLOYMENT_GUIDE.md](GITHUB_DEPLOYMENT_GUIDE.md)

Quick start:
```bash
# Using Gunicorn
gunicorn dusangire.wsgi:application --bind 0.0.0.0:8000

# Using Docker
docker build -t dusangire .
docker run -p 8000:8000 dusangire

# Using Heroku
heroku create dusangire
git push heroku main
```

## Configuration

### Environment Variables

Create a `.env` file with:
- `SECRET_KEY` - Django secret key
- `DEBUG` - Set to False in production
- `ALLOWED_HOSTS` - Comma-separated allowed hosts
- `DB_*` - Database credentials
- `EMAIL_*` - Email configuration
- `GOOGLE_OAUTH_*` - Google OAuth credentials (optional)

### Email Configuration

For development: Console backend (prints to console)
For production: Configure SMTP in `.env`

## Security

- CSRF protection enabled
- SQL injection prevention with ORM
- XSS protection in templates
- Authentication required for sensitive operations
- Role-based permission checks
- Secrets stored in environment variables

## Performance

- Optimized database queries with select_related/prefetch_related
- Pagination for large datasets
- Redis caching ready
- Efficient admin list displays

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests
4. Commit and push
5. Submit a pull request

## Support

For issues, questions, or feature requests:
1. Check existing documentation
2. Review admin interface
3. Check Django logs
4. Open an issue on GitHub

## License

All rights reserved.

---

**Version**: 1.0  
**Status**: Production Ready  
**Last Updated**: February 2025

