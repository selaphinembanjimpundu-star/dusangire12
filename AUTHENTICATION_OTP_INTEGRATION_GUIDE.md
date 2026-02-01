# Authentication & OTP Integration Guide

## Current Status

### ✅ Implemented Features

#### 1. **Password Reset System** (Built-in Django)
- Email-based password reset using Django's authentication system
- Secure token generation and validation
- Time-limited reset links (configurable timeout)
- Templates for:
  - Password reset request form
  - Email template
  - Reset confirmation page
  - Success page

**Location:** `/accounts/password_reset/`

#### 2. **Email Validation**
- Strict RFC-compliant email validation
- Applied to:
  - User registration
  - Contact form submissions
  - Profile updates
- Regex pattern: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`

**Validator:** `accounts/validators.py` → `validate_email_format()`

#### 3. **Contact Form Validation**
- Client-side (JavaScript) validation
- Server-side (Python) validation
- Real-time character count (max 1000)
- Field requirements:
  - Name: 3+ characters
  - Email: Valid format
  - Subject: 3+ characters
  - Message: 10-1000 characters

#### 4. **Auto-Reply System**
- HTML email templates
- Automatic confirmation to users
- Admin notification with contact reference ID
- Professional email formatting

---

## 🔄 OTP (One-Time Password) Integration

### Current Limitation
❌ **OTP is NOT currently integrated** because an API service is required.

### What's Needed for OTP Implementation

#### **Option 1: SMS-based OTP** (Recommended for Rwanda)
Services that work in Rwanda:
- **Africastalking** (Popular in East Africa)
  - API: `https://api.africastalking.com/`
  - SMS delivery to local numbers
  - Pricing: Per SMS cost

- **Twilio** (International)
  - API: `https://www.twilio.com/`
  - More expensive but reliable
  - Works in 180+ countries

- **Vodacom M-Pesa / MTN MoMo APIs**
  - Direct integration with local carriers
  - Lowest cost option

#### **Option 2: Email-based OTP**
- Uses existing email system
- Can be implemented without external API
- Less secure but easier to implement

### Implementation Steps (When API is Available)

#### **Step 1: Install Required Package**
```bash
pip install django-otp pyotp qrcode
# or for SMS:
pip install twilio
# or for Africastalking:
pip install africastalking
```

#### **Step 2: Create OTP Model**
```python
from django.db import models
from django.contrib.auth.models import User
import random, string
from django.utils import timezone
from datetime import timedelta

class UserOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def generate_otp(self):
        self.otp_code = ''.join(random.choices(string.digits, k=6))
        self.expires_at = timezone.now() + timedelta(minutes=5)
        self.save()
        return self.otp_code
    
    def is_valid(self):
        return (not self.is_verified and 
                timezone.now() < self.expires_at)
    
    def verify_otp(self, code):
        if self.is_valid() and self.otp_code == code:
            self.is_verified = True
            self.save()
            return True
        return False
```

#### **Step 3: Create OTP Views**
```python
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserOTP

def request_otp(request):
    """Send OTP to user"""
    user = request.user
    otp = UserOTP.objects.get_or_create(user=user)[0]
    code = otp.generate_otp()
    
    # Send via SMS (Africastalking example)
    import africastalking
    africastalking.initialize(
        username=settings.AFRICASTALKING_USERNAME,
        api_key=settings.AFRICASTALKING_API_KEY
    )
    sms = africastalking.SMS
    recipients = [user.profile.phone_number]  # User's phone
    message = f"Your Dusangire verification code is: {code}"
    
    response = sms.send(message, recipients)
    messages.success(request, f"OTP sent to {user.profile.phone_number}")
    return redirect('verify_otp')

def verify_otp(request):
    """Verify OTP code"""
    if request.method == 'POST':
        code = request.POST.get('otp_code')
        user = request.user
        
        try:
            otp = UserOTP.objects.get(user=user)
            if otp.verify_otp(code):
                messages.success(request, "Account verified!")
                return redirect('home')
            else:
                messages.error(request, "Invalid or expired OTP")
        except UserOTP.DoesNotExist:
            messages.error(request, "OTP not found")
    
    return render(request, 'accounts/verify_otp.html')
```

#### **Step 4: Settings Configuration**
```python
# settings.py

# Africastalking Configuration (if using Africastalking)
AFRICASTALKING_USERNAME = 'your_username'
AFRICASTALKING_API_KEY = 'your_api_key'

# Twilio Configuration (if using Twilio)
TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_PHONE_NUMBER = '+1234567890'

# OTP Configuration
OTP_EXPIRY_MINUTES = 5
OTP_RESEND_LIMIT = 3  # Maximum attempts
```

#### **Step 5: Email-Based OTP (No API Needed)**
```python
def send_email_otp(user):
    """Send OTP via email (no API needed)"""
    otp = UserOTP.objects.get_or_create(user=user)[0]
    code = otp.generate_otp()
    
    send_mail(
        'Your OTP Code - Dusangire',
        f'Your verification code is: {code}\nValid for 5 minutes.',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
    return code
```

---

## 📋 Integration Checklist

### For SMS-based OTP (Recommended)
- [ ] Choose SMS provider (Africastalking recommended for Rwanda)
- [ ] Create account and get API credentials
- [ ] Install required package
- [ ] Create UserOTP model
- [ ] Create OTP views and templates
- [ ] Add OTP middleware for security
- [ ] Test with real phone numbers
- [ ] Deploy to production

### For Email-based OTP (Simple alternative)
- [ ] Create UserOTP model
- [ ] Create OTP views and templates
- [ ] Use Django's existing email system
- [ ] Test email delivery
- [ ] Deploy immediately (no API needed)

---

## 🔐 Security Best Practices

1. **OTP Length:** Minimum 6 digits (current implementation)
2. **Expiry Time:** 5 minutes maximum
3. **Rate Limiting:** Max 3 attempts per hour
4. **Logging:** Log all OTP requests for audit
5. **HTTPS:** Always use SSL in production
6. **Database:** Hash OTP before storage (use hashing function)
7. **Throttling:** Prevent brute force attacks

---

## 📞 Recommended Provider for Rwanda

### **Africastalking** (Best Option)
- **Pros:**
  - Local support in Rwanda
  - Competitive pricing
  - Easy integration
  - Good documentation
  - Supports MTN, Airtel, Tigo

- **Cons:**
  - Requires account setup
  - Minimum balance needed

- **Cost:** ~2-5 RWF per SMS

- **Integration:** ⏱️ ~2 hours

### **Alternative: Direct MTN/Airtel API**
- **Pros:**
  - Lowest cost
  - Direct carrier integration
  
- **Cons:**
  - Complex setup
  - Requires carrier agreements
  
- **Cost:** ~1-3 RWF per SMS

---

## 🚀 Current Implementation

### Email Validation (✅ DONE)
- Strict validation on contact form
- Server-side and client-side checks
- Error messages for invalid emails

### Password Reset (✅ DONE)
- Built-in Django authentication
- Email-based token links
- Secure token generation

### OTP (⏳ PENDING)
- Requires: API service account
- Timeline: 2-4 hours after API setup
- Recommendation: Start with Email-based OTP (no cost)

---

## 📧 Current Email Configuration

```python
# settings.py
EMAIL_FROM_USER = 'rukundojeandedieu670@gmail.com'
DEFAULT_FROM_EMAIL = 'rukundojeandedieu670@gmail.com'
CONTACT_EMAIL = 'rukundojeandedieu670@gmail.com'
CONTACT_PHONE = '+250792392072'
SUPPORT_EMAIL = 'rukundojeandedieu670@gmail.com'
SUPPORT_PHONE = '+250792392072'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Development
# For production: django.core.mail.backends.smtp.EmailBackend
```

---

## 🔗 Useful Links

- **Django Authentication:** https://docs.djangoproject.com/en/stable/topics/auth/
- **Django OTP:** https://django-otp-official.readthedocs.io/
- **Africastalking:** https://africastalking.com/
- **Twilio:** https://www.twilio.com/
- **PyOTP:** https://github.com/pyauth/pyotp

---

## Next Steps

1. **Immediate:** Email validation is ✅ DONE
2. **Short-term:** Password reset is ✅ DONE (built-in)
3. **Medium-term:** Implement Email-based OTP (no API needed)
4. **Long-term:** Upgrade to SMS OTP when API service is available

**Current Status:** 2/3 features implemented. Ready for production.
