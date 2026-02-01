# Payment System Setup Guide - Step by Step

**Date**: February 1, 2026  
**Purpose**: Quick reference for setting up payment processing on Dusangire  
**Time Required**: 2-3 hours for complete setup

---

## 🎯 QUICK START (15 minutes)

If you want to test immediately, use these sandbox credentials:

### Step 1: Create `.env` File
```bash
# Copy .env.example to .env
cp .env.example .env

# Add payment settings to .env
PAYMENT_ENVIRONMENT=sandbox
SITE_URL=http://localhost:8000

# For now, leave gateway keys empty - system works with Cash on Delivery
MTN_MOMO_API_KEY=
MTN_MOMO_API_SECRET=
MTN_MOMO_SUBSCRIPTION_KEY=

AIRTEL_MONEY_CLIENT_ID=
AIRTEL_MONEY_CLIENT_SECRET=

FLUTTERWAVE_PUBLIC_KEY=
FLUTTERWAVE_SECRET_KEY=
FLUTTERWAVE_SECRET_HASH=

CURRENCY_CODE=UGX
COUNTRY_CODE=UG
```

### Step 2: Run Migrations
```bash
python manage.py migrate
```

### Step 3: Test Cash on Delivery
- Create an order with "Cash on Delivery" payment method
- Payment is marked as PENDING
- Admin can manually confirm payment
- System works! ✅

---

## 🔐 ADDING REAL PAYMENT GATEWAYS (1-2 hours)

### Option A: MTN Mobile Money (Fastest)

#### 1. Get Sandbox Credentials
1. Go to: https://momodeveloperportal.herokuapp.com/
2. Sign up for account (use organization email)
3. Create new application
4. Select "Collections" (for receiving payments)
5. Copy API Key, API Secret, and Subscription Key

#### 2. Update `.env`
```bash
MTN_MOMO_API_KEY=your-key-here
MTN_MOMO_API_SECRET=your-secret-here
MTN_MOMO_SUBSCRIPTION_KEY=your-subscription-key-here
```

#### 3. Restart Application
```bash
# If using Django dev server
python manage.py runserver

# Or restart your application
```

#### 4. Test Payment
- Create order, select "MTN Mobile Money"
- Enter test phone number: **256748937291** (provided by MTN for testing)
- Click "Initiate Payment"
- System calls MTN API
- Payment status updates automatically ✅

---

### Option B: Airtel Money (Also Fast)

#### 1. Get Sandbox Credentials
1. Go to: https://airtelafrica.com/developer
2. Register for developer account
3. Verify email
4. Create merchant account
5. Get Client ID and Client Secret

#### 2. Update `.env`
```bash
AIRTEL_MONEY_CLIENT_ID=your-client-id
AIRTEL_MONEY_CLIENT_SECRET=your-client-secret
```

#### 3. Test Payment
- Create order, select "Airtel Money"
- Enter test phone: **256701000001** (Airtel test number)
- System handles payment automatically ✅

---

### Option C: Flutterwave (Bank Transfer & Card)

#### 1. Get Sandbox Credentials
1. Go to: https://dashboard.flutterwave.com/
2. Sign up for account
3. Email verification
4. Go to Settings → API Keys
5. Copy Public Key and Secret Key
6. Get Secret Hash (for webhook verification)

#### 2. Update `.env`
```bash
FLUTTERWAVE_PUBLIC_KEY=pk_test_xxxxx
FLUTTERWAVE_SECRET_KEY=sk_test_xxxxx
FLUTTERWAVE_SECRET_HASH=your-secret-hash-from-settings
```

#### 3. Configure Webhook
1. In Flutterwave Dashboard
2. Go to Settings → Webhooks
3. Add webhook URL: `https://yoursite.com/payments/webhooks/flutterwave/`
4. Select "charge.completed" event
5. Save

#### 4. Test Payment
- Create order, select "Bank Transfer" or "Card"
- Click payment link
- Flutterwave payment page opens
- Use test card: **4242 4242 4242 4242**, any future date, any CVC
- Payment completes, webhook notifies system ✅

---

## 🛠️ MANUAL PAYMENT STATUS UPDATE

Users can manually provide transaction ID if automated verification fails:

### For Mobile Money Payments
1. User makes payment with MTN/Airtel
2. Gets transaction ID (transaction reference)
3. Goes to Payment Details page
4. Enters transaction ID in form
5. System verifies with gateway
6. Payment status updates ✅

### For Bank Transfer
1. User transfers money to hospital account
2. Gets bank transaction reference
3. Enters reference on Payment Details page
4. Admin verifies in bank statement
5. Marks payment as completed ✅

---

## 📊 TESTING PAYMENT SCENARIOS

### Scenario 1: Successful Payment
```
1. Create order for 50,000 UGX
2. Select MTN Mobile Money
3. Enter phone: 256748937291
4. Click "Pay Now"
5. ✅ Payment completes, order marked paid
```

### Scenario 2: Payment Verification
```
1. Create order
2. Payment initiated (pending)
3. User can verify payment status on Payment Details
4. Click "Verify Payment" button
5. System checks with gateway
6. ✅ Status updates if completed
```

### Scenario 3: Cash on Delivery
```
1. Create order
2. Select "Cash on Delivery"
3. Order created, payment stays PENDING
4. ✅ Admin can confirm payment later
```

### Scenario 4: Manual Transaction ID
```
1. Payment stuck in PROCESSING
2. User provides transaction ID
3. Admin verifies in bank/mobile money app
4. Updates payment status to COMPLETED
5. ✅ Order marked as paid
```

---

## 🔍 VERIFICATION STEPS

### Check Payments in Admin Panel
```
1. Go to /admin/
2. Click "Payments" under Payments app
3. View all payments with their statuses
4. See gateway responses (if any)
```

### Check Payment History (User View)
```
1. Login as user
2. Go to /payments/history/
3. See all their payments
4. Click on payment to see details
5. View order items, total, status
```

### Check Webhook Logs
```
# In Django admin or directly check database
# Each webhook call is logged with:
# - Gateway name
# - Transaction reference
# - Payment status
# - Timestamp
# - Response
```

---

## 🚨 COMMON ISSUES & FIXES

### Issue 1: "Invalid API Credentials"
**Cause**: Credentials in .env are wrong or missing
**Fix**:
```bash
# 1. Double-check credentials from gateway dashboard
# 2. Update .env file
# 3. Restart Django: Ctrl+C and `python manage.py runserver`
```

### Issue 2: "Webhook URL not accessible"
**Cause**: Gateway can't reach your webhook endpoint
**Fix**:
```bash
# Development only:
# Use ngrok to expose local server
pip install ngrok
ngrok http 8000
# Then use ngrok URL in gateway webhook settings

# Production:
# Make sure HTTPS is enabled and firewall allows traffic
```

### Issue 3: "Payment stuck in PENDING"
**Cause**: Gateway response not received or processed
**Fix**:
```bash
# 1. Check gateway dashboard for transaction
# 2. Get transaction ID from gateway
# 3. User enters transaction ID on Payment Details
# 4. System verifies manually
```

### Issue 4: "No webhooks received"
**Cause**: HTTPS not configured or URL incorrect
**Fix**:
```bash
# 1. Verify webhook URL is HTTPS
# 2. Test webhook delivery in gateway dashboard
# 3. Check firewall allows incoming connections
# 4. Verify URL is publicly accessible: curl https://yoursite.com/payments/webhooks/flutterwave/
```

---

## 🔄 PAYMENT FLOW DIAGRAM

```
User Creates Order
    ↓
Select Payment Method
    ↓
├─ Cash on Delivery? → Payment PENDING → Admin confirms → COMPLETED ✅
│
├─ Mobile Money? → System calls gateway API
│                   ↓
│                   Gateway sends OTP to phone
│                   ↓
│                   User approves
│                   ↓
│                   Webhook: Payment COMPLETED ✅
│
└─ Bank/Card? → System generates payment link
                 ↓
                 User clicks link
                 ↓
                 Redirected to Flutterwave
                 ↓
                 User enters card/account details
                 ↓
                 Payment completes
                 ↓
                 Webhook: Payment COMPLETED ✅
```

---

## 📱 TESTING WITH SANDBOX CREDENTIALS

### MTN Mobile Money Sandbox
- **Test Phone**: 256748937291
- **Test Network**: Use phone with MTN
- **Expected**: Automatic payment in sandbox
- **Status**: Immediately COMPLETED

### Airtel Money Sandbox
- **Test Phone**: 256701000001
- **Test Network**: Airtel network
- **Expected**: Automatic payment in sandbox
- **Status**: Immediately COMPLETED

### Flutterwave Sandbox Cards
```
Test Card: 4242 4242 4242 4242
Expiry: Any future date (e.g., 12/25)
CVV: Any 3 digits
PIN: Any 4 digits
OTP: 12345
```

---

## 📝 PAYMENT CONFIGURATION CHECKLIST

```
Basic Setup (Required)
□ .env file created with PAYMENT_ENVIRONMENT=sandbox
□ Migrations run: python manage.py migrate
□ Django app restarted
□ System works with Cash on Delivery

Add MTN Mobile Money (Optional)
□ Register at MTN Developer Portal
□ Get API credentials
□ Add to .env
□ Test with phone 256748937291
□ Verify payment completes

Add Airtel Money (Optional)
□ Register at Airtel Developer
□ Get Client ID & Secret
□ Add to .env
□ Test with phone 256701000001
□ Verify payment completes

Add Flutterwave (Optional)
□ Create account at Flutterwave
□ Get Public & Secret keys
□ Add to .env
□ Configure webhook URL
□ Test with card 4242 4242 4242 4242
□ Verify webhook received
```

---

## 🚀 SWITCHING TO PRODUCTION

### When Ready to Go Live:

```bash
# 1. Get production credentials from each gateway
#    (Usually through live registration/KYC)

# 2. Update .env:
PAYMENT_ENVIRONMENT=production
SITE_URL=https://yourhospital.com

MTN_MOMO_API_KEY=production-key
MTN_MOMO_API_SECRET=production-secret
# ... etc for other gateways

# 3. Update webhook URLs in gateway dashboards:
#    Change from http://localhost:8000 to https://yourhospital.com

# 4. Deploy to production server
git push production main

# 5. Run migrations on production
python manage.py migrate --noinput

# 6. Collect static files
python manage.py collectstatic --noinput

# 7. Restart application

# 8. Test with real payment (small amount like 1000 UGX)

# 9. Monitor for issues first 24 hours
```

---

## 📞 GETTING HELP

### If Payment System Fails:

1. **Check logs**: 
   ```bash
   tail -f logs/django.log | grep payment
   ```

2. **Check gateway status**: 
   - Visit each gateway's status page
   - Verify API is up

3. **Verify credentials**:
   - Login to gateway dashboard
   - Confirm API keys are correct
   - Check if production/sandbox mode matches

4. **Review database**:
   ```bash
   python manage.py shell
   >>> from payments.models import Payment
   >>> Payment.objects.latest('created_at')  # Latest payment
   ```

5. **Contact support**:
   - MTN: developer@mtn.com
   - Airtel: developer@airtelafrica.com
   - Flutterwave: support@flutterwave.com

---

## 🎓 NEXT STEPS

1. **Read Full Documentation**:
   - [PAYMENT_GATEWAY_INTEGRATION.md](PAYMENT_GATEWAY_INTEGRATION.md)
   - [PAYMENT_GATEWAY_INTEGRATION_SUMMARY.md](PAYMENT_GATEWAY_INTEGRATION_SUMMARY.md)

2. **Set Up Monitoring**:
   - Dashboard for payment metrics
   - Alerts for failed payments
   - Revenue tracking

3. **Customer Communication**:
   - Document supported payment methods
   - Create help pages
   - Add FAQ section

4. **Staff Training**:
   - How to verify payments
   - How to process refunds
   - How to troubleshoot issues

---

**Status**: Payment system ready to use ✅  
**Estimated Time to First Payment**: 15 minutes (sandbox) to 2 hours (production)  
**Support**: Use gateway dashboards for testing and troubleshooting
