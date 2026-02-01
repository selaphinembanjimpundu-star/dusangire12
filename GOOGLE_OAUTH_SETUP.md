# Google OAuth Login Setup Guide

## Overview
This guide explains how to set up Google OAuth login for the Dusangire application using django-allauth.

## What Was Added

### 1. Python Packages
The following packages were added to `requirements.txt`:
- `django-allauth>=0.57.0` - OAuth2 authentication framework
- `django-cors-headers>=4.3.1` - CORS support for OAuth
- `google-auth-oauthlib>=1.1.0` - Google OAuth library
- `google-auth>=2.25.0` - Google authentication

### 2. Django Configuration

#### Settings (`dusangire/settings.py`)
- Added `django.contrib.sites` to INSTALLED_APPS (required by allauth)
- Added allauth apps:
  - `allauth`
  - `allauth.account`
  - `allauth.socialaccount`
  - `allauth.socialaccount.providers.google`
- Added `corsheaders` middleware
- Configured authentication backends to support both Django and allauth
- Set SITE_ID = 1 (required for allauth)
- Configured Google OAuth provider settings
- Added CORS allowed origins

#### URLs (`dusangire/urls.py`)
- Added `path('accounts/', include('allauth.urls'))` to include allauth URL patterns

#### Login Template (`templates/accounts/login.html`)
- Added Google login button with icon
- Button links to Google OAuth endpoint
- Text: "Continue with Google"
- Positioned above traditional username/password login

### 3. Authentication Flow
New authentication backends:
```python
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Django built-in
    'allauth.account.auth_backends.AuthenticationBackend',  # OAuth support
]
```

## Step-by-Step Setup

### Step 1: Install Python Packages
```bash
pip install -r requirements.txt
```

### Step 2: Create Google OAuth Application
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable Google+ API:
   - Click "APIs & Services" → "Library"
   - Search for "Google+ API"
   - Click "Enable"
4. Create OAuth 2.0 Credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Choose "Web application"
   - Add authorized JavaScript origins:
     ```
     http://localhost:8000
     http://127.0.0.1:8000
     https://yourdomain.com  (for production)
     ```
   - Add authorized redirect URIs:
     ```
     http://localhost:8000/accounts/google/login/callback/
     http://127.0.0.1:8000/accounts/google/login/callback/
     https://yourdomain.com/accounts/google/login/callback/  (for production)
     ```
   - Copy your Client ID and Client Secret

### Step 3: Configure Environment Variables
Create or update `.env` file in project root:
```env
GOOGLE_OAUTH_CLIENT_ID=your_client_id_here
GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret_here
```

### Step 4: Update Settings
The settings are already configured to use environment variables:
```python
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'APP': {
            'client_id': os.getenv('GOOGLE_OAUTH_CLIENT_ID', ''),
            'secret': os.getenv('GOOGLE_OAUTH_CLIENT_SECRET', ''),
            'key': ''
        }
    }
}
```

Update settings.py to load from environment:
```python
import os
from decouple import config

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'APP': {
            'client_id': config('GOOGLE_OAUTH_CLIENT_ID', default=''),
            'secret': config('GOOGLE_OAUTH_CLIENT_SECRET', default=''),
            'key': ''
        }
    }
}
```

### Step 5: Run Migrations
```bash
python manage.py migrate
```

### Step 6: Create Site in Django Admin
1. Run the development server:
   ```bash
   python manage.py runserver
   ```
2. Go to `http://localhost:8000/admin/`
3. Navigate to "Sites" section
4. Edit the default site:
   - Domain: `localhost:8000` (dev) or your actual domain (production)
   - Display name: `Dusangire`
5. Save

### Step 7: Register Google OAuth App in Django
1. Go to Admin → "Social applications"
2. Click "Add Social application"
3. Fill in the form:
   - **Provider**: Google
   - **Name**: Google OAuth
   - **Client id**: Paste your Google Client ID
   - **Secret key**: Paste your Google Client Secret
   - **Sites**: Select your site (Dusangire)
4. Save

## Features

### Automatic Account Creation
When a user logs in with Google:
- Account is automatically created (if enabled)
- Email is verified automatically
- User profile is created with Google data
- User is linked to their Google account

### Multi-Role Support
Users can login with Google and maintain their role:
- Customer
- Nutritionist
- Kitchen Staff
- Delivery Personnel
- Admin

The role is automatically assigned based on user type stored in the database.

### Security Features
- HTTPS required in production
- Secure OAuth token handling
- CSRF protection
- Session-based authentication
- Email verification support

## Testing

### Local Testing
1. Start development server:
   ```bash
   python manage.py runserver
   ```
2. Navigate to login page: `http://localhost:8000/accounts/login/`
3. Click "Continue with Google"
4. Authenticate with your Google account
5. You should be redirected to your role-specific dashboard

### Production Deployment
Before deploying to production:
1. Update authorized origins and redirect URIs in Google Console
2. Set correct SITE_URL in settings.py
3. Update environment variables on server
4. Enable HTTPS
5. Update DEBUG = False
6. Configure allowed hosts

## Configuration Options

### Customization
Edit settings.py to customize behavior:

```python
# Auto-signup on first OAuth login
SOCIALACCOUNT_AUTO_SIGNUP = True

# Require email
ACCOUNT_EMAIL_REQUIRED = True

# Email verification
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'  # or 'optional', 'mandatory'

# Store additional data
SOCIALACCOUNT_STORE_TOKENS = True
```

### User Data Retrieved from Google
- Email
- First name
- Last name
- Profile picture
- Locale
- Gender (if available)

## Troubleshooting

### "Invalid Client" Error
- Verify Client ID and Client Secret are correct
- Check that domain is in authorized origins
- Ensure environment variables are loaded

### Redirect URI Mismatch
- Verify redirect URI matches exactly in Google Console
- Include protocol (http/https)
- Include full path: `/accounts/google/login/callback/`

### Site Not Found
- Run migrations: `python manage.py migrate`
- Add site in Django admin
- Ensure SITE_ID = 1 in settings

### Account Not Created
- Check SOCIALACCOUNT_AUTO_SIGNUP = True
- Verify email is valid
- Check database permissions

## Additional Resources

- [django-allauth Documentation](https://django-allauth.readthedocs.io/)
- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Django Authentication](https://docs.djangoproject.com/en/5.2/topics/auth/)

## Next Steps

1. ✅ Install packages
2. ✅ Create Google OAuth app
3. ✅ Add credentials to environment
4. ✅ Run migrations
5. ✅ Configure site in admin
6. ✅ Test login flow
7. ✅ Deploy to production

## Files Modified

1. **requirements.txt** - Added OAuth packages
2. **dusangire/settings.py** - Added OAuth configuration
3. **dusangire/urls.py** - Added allauth URLs
4. **templates/accounts/login.html** - Added Google login button

## Support

For issues or questions:
1. Check django-allauth documentation
2. Review Google OAuth setup steps
3. Verify all credentials are correct
4. Check Django logs for errors
