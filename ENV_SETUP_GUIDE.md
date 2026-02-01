# Environment Variables Setup for Google OAuth

## Required Environment Variables

Create a `.env` file in the project root (same directory as `manage.py`) with the following variables:

```env
# Google OAuth Configuration
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id_here
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret_here

# Django Settings (Optional but Recommended)
DEBUG=True
SECRET_KEY=your_django_secret_key

# Database (if using environment variables)
DB_NAME=dusangire
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Email Configuration (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

# Payment Gateway Keys (Optional)
MTN_MOMO_API_KEY=your_mtn_api_key
MTN_MOMO_API_SECRET=your_mtn_api_secret
FLUTTERWAVE_PUBLIC_KEY=your_flutterwave_key
FLUTTERWAVE_SECRET_KEY=your_flutterwave_secret
```

## Getting Google OAuth Credentials

### 1. Create Google Cloud Project
- Visit [Google Cloud Console](https://console.cloud.google.com/)
- Click "Select a Project" → "New Project"
- Enter project name: "Dusangire"
- Click "Create"

### 2. Enable Google+ API
- In Cloud Console, search for "Google+ API"
- Click on it and then click "Enable"

### 3. Create OAuth 2.0 Credentials
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. You may need to create a consent screen first:
   - Choose "External" user type
   - Click "Create"
   - Fill in app name: "Dusangire"
   - Add your email
   - Add scopes: `email`, `profile`
   - Save and continue

4. After consent screen, create OAuth client:
   - Application type: "Web application"
   - Name: "Dusangire Web App"
   - Add Authorized JavaScript origins:
     ```
     http://localhost:8000
     http://127.0.0.1:8000
     http://localhost:3000
     https://yourdomain.com (for production)
     ```
   - Add Authorized redirect URIs:
     ```
     http://localhost:8000/accounts/google/login/callback/
     http://127.0.0.1:8000/accounts/google/login/callback/
     https://yourdomain.com/accounts/google/login/callback/ (for production)
     ```
   - Click "Create"

### 4. Copy Credentials
- Copy your **Client ID** and **Client Secret**
- Add them to `.env` file:
  ```env
  GOOGLE_OAUTH_CLIENT_ID=your_client_id
  GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret
  ```

## Environment Variable Locations

### Development
`.env` file in project root:
```
Dusangire/
├── manage.py
├── .env  ← Create here
├── Dusangire/
│   └── settings.py
```

### Production (Heroku/Railway/Azure)
Set environment variables in your platform's dashboard:
- Heroku: Settings → Config Vars
- Railway: Variables section
- Azure: Application Settings
- AWS: Parameter Store or Secrets Manager

## Verifying Environment Setup

### 1. Test Environment Variables Load
```bash
python manage.py shell
```

In the Python shell:
```python
from django.conf import settings
print(settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id'])
# Should print your Client ID, not empty string
```

### 2. Run Migrations
```bash
python manage.py migrate
```

### 3. Create Superuser
```bash
python manage.py createsuperuser
```

### 4. Configure Site in Admin
```bash
python manage.py runserver
```

Visit `http://localhost:8000/admin/`
- Go to "Sites"
- Edit the default site
- Domain: `localhost:8000` (or your actual domain)
- Display name: `Dusangire`
- Save

### 5. Add Social Application
In Django Admin:
- Go to "Social applications"
- Click "Add Social application"
- Provider: `Google`
- Name: `Google OAuth`
- Client id: Paste your Google Client ID
- Secret key: Paste your Google Client Secret
- Site: Select `Dusangire` (localhost:8000 or your domain)
- Click "Save"

## Troubleshooting

### Error: "GOOGLE_OAUTH_CLIENT_ID is empty"
- Check `.env` file exists in project root
- Verify format: `GOOGLE_OAUTH_CLIENT_ID=your_id` (no quotes)
- Restart Django development server
- Restart Python shell

### Error: "Invalid Client"
- Verify Client ID and Secret are correct
- Copy them again from Google Cloud Console
- Remove any accidental whitespace in `.env`
- Restart server

### Error: "Redirect URI Mismatch"
- Check Google Cloud Console → Credentials
- Verify redirect URIs match exactly:
  - Include protocol (http or https)
  - Include full path: `/accounts/google/login/callback/`
  - Include trailing slash

### Error: "Site not found"
- Run migrations: `python manage.py migrate`
- Create site in Django admin (see step 4 above)
- Ensure SITE_ID = 1 in settings.py

## Security Notes

### DO's
- ✅ Keep `.env` file out of version control (add to `.gitignore`)
- ✅ Use strong SECRET_KEY in production
- ✅ Enable HTTPS in production
- ✅ Use environment variables for all secrets
- ✅ Rotate credentials regularly
- ✅ Restrict redirect URIs to your domains only

### DON'Ts
- ❌ Don't commit `.env` to Git
- ❌ Don't share credentials in code or comments
- ❌ Don't use same credentials for dev and prod
- ❌ Don't allow all hosts in production (DEBUG=False)
- ❌ Don't use http in production (only https)

## Example .env File

```env
# Core Django Settings
DEBUG=True
SECRET_KEY=django-insecure-40^5e(c&86(8ae3np5&ew%r!z1ifz&d)ex@0i2r3=w3%q3yko2

# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=123456789-abcdefghijklmnopqrstuvwxyz.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxxxxxxxxx

# Database (PostgreSQL Example)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=dusangire_db
DB_USER=postgres
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Email (Gmail Example)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_specific_password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@nourishlink.com

# Payment Gateways (Optional)
MTN_MOMO_API_KEY=your_mtn_key
MTN_MOMO_SUBSCRIPTION_KEY=your_mtn_sub_key
FLUTTERWAVE_PUBLIC_KEY=FLWPUBK_TEST_xxxxx
FLUTTERWAVE_SECRET_KEY=FLWSECK_TEST_xxxxx
```

## Next Steps

1. ✅ Create `.env` file
2. ✅ Add Google OAuth credentials
3. ✅ Run migrations
4. ✅ Create superuser
5. ✅ Configure site in admin
6. ✅ Add social application
7. ✅ Test login flow

## Support

If you need help with setup:
1. Check [django-allauth docs](https://django-allauth.readthedocs.io/)
2. Review [Google OAuth documentation](https://developers.google.com/identity)
3. Check Django logs for error messages
4. Ensure all environment variables are set correctly
