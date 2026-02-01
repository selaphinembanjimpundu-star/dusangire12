# Payment System Architecture & Reference

**Date**: February 1, 2026  
**Type**: Technical Architecture Document  
**Audience**: Developers & DevOps

---

## 🏗️ SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                     Dusangire Payment System                 │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│  User Orders Food    │
└──────────┬───────────┘
           ↓
┌──────────────────────────────────────────┐
│  1. Select Payment Method                │
│     - Cash on Delivery                   │
│     - MTN Mobile Money                   │
│     - Airtel Money                       │
│     - Bank Transfer                      │
│     - Card Payment                       │
└──────────┬───────────────────────────────┘
           ↓
┌──────────────────────────────────────────┐
│  2. Create Payment Record                │
│     (Database Entry)                     │
└──────────┬───────────────────────────────┘
           ↓
        ╔═══════════════════════════════════════════════════════════╗
        ║  3. Payment Processing by Gateway                         ║
        ╠═══════════════════════════════════════════════════════════╣
        ║                                                           ║
        ║  ┌────────────────────────────────────────────────┐      ║
        ║  │ CASH ON DELIVERY                              │      ║
        ║  │ No API call needed                            │      ║
        ║  │ Status: PENDING (admin confirms)             │      ║
        ║  └────────────────────────────────────────────────┘      ║
        ║                                                           ║
        ║  ┌────────────────────────────────────────────────┐      ║
        ║  │ MTN MOBILE MONEY                               │      ║
        ║  │ 1. API Call to MTN gateway                    │      ║
        ║  │ 2. OAuth authentication                       │      ║
        ║  │ 3. Payment initiation request sent            │      ║
        ║  │ 4. User gets OTP on phone                     │      ║
        ║  │ 5. User approves payment                      │      ║
        ║  │ 6. Webhook callback received                  │      ║
        ║  │ 7. Status updated to COMPLETED               │      ║
        ║  └────────────────────────────────────────────────┘      ║
        ║                                                           ║
        ║  ┌────────────────────────────────────────────────┐      ║
        ║  │ AIRTEL MONEY                                   │      ║
        ║  │ 1. API Call to Airtel gateway                 │      ║
        ║  │ 2. OAuth authentication                       │      ║
        ║  │ 3. Payment initiation request sent            │      ║
        ║  │ 4. User gets OTP on phone                     │      ║
        ║  │ 5. User approves payment                      │      ║
        ║  │ 6. Webhook callback received                  │      ║
        ║  │ 7. Status updated to COMPLETED               │      ║
        ║  └────────────────────────────────────────────────┘      ║
        ║                                                           ║
        ║  ┌────────────────────────────────────────────────┐      ║
        ║  │ BANK TRANSFER & CARD (Flutterwave)            │      ║
        ║  │ 1. Generate payment link with Flutterwave API│      ║
        ║  │ 2. Redirect user to Flutterwave page          │      ║
        ║  │ 3. User enters card/bank details              │      ║
        ║  │ 4. Payment processed by Flutterwave           │      ║
        ║  │ 5. Redirect back to hospital site             │      ║
        ║  │ 6. Webhook: Payment status update             │      ║
        ║  │ 7. Status updated to COMPLETED               │      ║
        ║  └────────────────────────────────────────────────┘      ║
        ║                                                           ║
        ╚═══════════════════════════════════════════════════════════╝
           ↓
┌──────────────────────────────────────────┐
│  4. Update Order Status                  │
│     - Payment: COMPLETED                 │
│     - Order: PAID                        │
│     - Generate Invoice                   │
└──────────┬───────────────────────────────┘
           ↓
┌──────────────────────────────────────────┐
│  5. Confirmation to User                 │
│     - Show receipt                       │
│     - Send confirmation email            │
│     - Order ready for fulfillment        │
└──────────────────────────────────────────┘
```

---

## 🗂️ FILE STRUCTURE

```
payments/
├── models.py                    # Payment data models
├── views.py                     # Payment views & endpoints
├── urls.py                      # URL routing
├── gateways.py                  # Payment gateway integrations
├── webhooks.py                  # Webhook handlers from gateways
├── forms.py                     # Payment forms
├── admin.py                     # Django admin configuration
├── apps.py                      # App configuration
└── migrations/
    ├── 0001_initial.py         # Initial payment models
    └── 0002_*.py               # Gateway integration fields

templates/payments/
├── payment_confirmation.html    # Order confirmed, payment done
├── payment_detail.html          # Payment details page
├── payment_history.html         # User's payment history
└── receipt.html                 # Payment receipt/invoice

tests/
├── test_payment_gateways.py    # Gateway integration tests
├── test_payment_models.py      # Payment model tests
└── test_payment_views.py       # Payment view tests

docs/
├── PAYMENT_FINALIZATION_CHECKLIST.md  # This document
├── PAYMENT_SETUP_GUIDE.md             # Setup instructions
└── PAYMENT_GATEWAY_INTEGRATION.md     # Full integration guide
```

---

## 📊 DATABASE SCHEMA

### Payment Model
```python
class Payment(models.Model):
    # Identifiers
    id                  # Auto-generated ID
    payment_id          # Unique payment reference
    
    # Relations
    order               # ForeignKey → Order (one-to-one)
    subscription        # ForeignKey → Subscription (optional)
    
    # Payment Details
    amount              # Decimal amount
    currency            # Currency code (e.g., 'UGX')
    payment_method      # Choice: MTN, Airtel, Bank, Card, COD
    
    # Status Tracking
    status              # Choice: PENDING, PROCESSING, COMPLETED, FAILED, etc.
    transaction_id      # Reference from payment gateway
    phone_number        # For mobile money payments
    account_number      # For bank transfers
    
    # Gateway Integration
    gateway_name        # Which gateway processed (e.g., 'flutterwave')
    gateway_response    # JSON response from gateway
    payment_link        # URL for redirect-based payments
    
    # Timestamps
    created_at          # When payment created
    updated_at          # Last update
    paid_at             # When payment completed
    
    # Notes
    notes               # Admin notes
```

---

## 🔄 API FLOW

### Step 1: Payment Initiation
```
Request: POST /orders/checkout/
Body: {
    "items": [...],
    "payment_method": "mtn_mobile_money",
    "phone_number": "+256123456789"
}

Response: {
    "success": true,
    "order_id": 123,
    "payment_id": 456,
    "status": "pending",
    "next_url": "/payments/confirmation/456/"
}
```

### Step 2: Payment Processing

**For Mobile Money (MTN/Airtel):**
```
Internal Flow:
1. PaymentGatewayService.initiate_payment(payment)
2. MTNMobileMoneyGateway or AirtelMoneyGateway called
3. OAuth token requested from gateway
4. Payment API called with amount, phone, reference
5. Response returned with transaction ID
6. Payment saved to database with status "PROCESSING"
7. User shown "Please approve on your phone" message
```

**For Card/Bank (Flutterwave):**
```
Internal Flow:
1. PaymentGatewayService.initiate_payment(payment)
2. FlutterwaveGateway called
3. Payment link generated
4. User redirected to Flutterwave
5. User completes payment at Flutterwave
6. Flutterwave redirects back: /payments/callback/
7. Webhook received later with payment status
```

### Step 3: Webhook Processing
```
Webhook Request (from gateway):
POST /payments/webhooks/flutterwave/
Headers: {"X-Rave-Signature": "hash..."}
Body: {
    "event": "charge.completed",
    "data": {
        "tx_ref": "ORDER_12345_456",
        "status": "successful",
        "amount": 50000,
        "currency": "UGX"
    }
}

Processing:
1. Verify webhook signature
2. Extract payment ID from tx_ref
3. Lookup payment in database
4. Update status to COMPLETED
5. Update order status to PAID
6. Return success response
```

---

## 🔐 SECURITY IMPLEMENTATION

### API Key Protection
```python
# Environment variables (.env) - never in code
MTN_MOMO_API_KEY=...
AIRTEL_MONEY_CLIENT_SECRET=...
FLUTTERWAVE_SECRET_KEY=...

# Read in settings.py
from decouple import config
MTN_MOMO_API_KEY = config('MTN_MOMO_API_KEY')
```

### Webhook Signature Verification
```python
# Flutterwave Example
def verify_flutterwave_webhook(signature, data):
    secret_hash = settings.FLUTTERWAVE_SECRET_HASH
    expected_hash = hmac.new(
        secret_hash.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return signature == expected_hash

# If signature doesn't match, reject webhook
```

### HTTPS Requirements
```
# All payment operations must use HTTPS
# Gateways will reject HTTP webhooks
# Configure in production:
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Input Validation
```python
# Validate phone numbers
if payment_method == 'mtn_mobile_money':
    if not phone_number or len(phone_number) < 10:
        raise ValidationError("Invalid phone number")

# Validate amounts
if amount <= 0:
    raise ValidationError("Amount must be positive")

# Validate currency matches configuration
if currency != settings.CURRENCY_CODE:
    raise ValidationError(f"Currency must be {settings.CURRENCY_CODE}")
```

---

## 🔧 GATEWAY INTEGRATION DETAILS

### MTN Mobile Money

**Authentication Flow:**
```
1. Get OAuth token:
   POST /oauth/token/v2
   client_id: MTN_MOMO_API_KEY
   client_secret: MTN_MOMO_API_SECRET
   
2. Token received: access_token=...
3. Use token for payment requests
4. Token expires, get new one
```

**Payment Initiation:**
```
POST /mtn/momo/v1_0/requesttopay
Authorization: Bearer {access_token}
X-Target-Environment: sandbox/production
X-Callback-Url-Base: https://yourdomain.com

Body:
{
    "amount": "50000",
    "currency": "UGX",
    "externalId": "ORDER_12345_456",
    "payee": {
        "partyIdType": "MSISDN",
        "partyId": "+256123456789"
    },
    "payer": {
        "partyIdType": "MSISDN",
        "partyId": "+256123456789"
    },
    "payerMessage": "Hospital meal payment",
    "payeeNote": "Payment for order 12345"
}

Response:
{
    "financialTransactionId": "MTN_TRANSACTION_ID"
}
```

**Payment Verification:**
```
GET /mtn/momo/v1_0/requesttopay/{transactionId}
Authorization: Bearer {access_token}

Response:
{
    "financialTransactionId": "MTN_TRANSACTION_ID",
    "status": "SUCCESSFUL|FAILED|PENDING"
}
```

### Airtel Money

**Similar OAuth flow** but with:
```
Token URL: https://api.airtel.africa/standard/v1/authentication
Payment URL: https://api.airtel.africa/standard/v1/payments
```

### Flutterwave

**Payment Link Generation:**
```
POST https://api.flutterwave.com/v3/charges?type=redirect

Body:
{
    "tx_ref": "ORDER_12345_456",
    "amount": 50000,
    "currency": "UGX",
    "redirect_url": "https://yourdomain.com/payments/callback/",
    "customer": {
        "email": "user@hospital.com",
        "name": "John Doe",
        "phone_number": "+256123456789"
    },
    "customizations": {
        "title": "Hospital Payment",
        "description": "Meal payment for order 12345"
    }
}

Response:
{
    "status": "success",
    "data": {
        "link": "https://checkout.flutterwave.com/v3/..."
    }
}
```

---

## 📈 MONITORING & LOGGING

### Log Structure
```python
# When payment initiated
logger.info(f"Payment initiated: ID={payment_id}, Method={payment_method}, Amount={amount}")

# When gateway called
logger.debug(f"Calling {gateway_name} API: {request_type}")

# When webhook received
logger.info(f"Webhook received: Gateway={gateway_name}, Transaction={transaction_id}, Status={status}")

# On errors
logger.error(f"Payment processing failed: {error_message}", exc_info=True)
```

### Metrics to Track
```
- Total payments by method
- Payment success rate by gateway
- Average payment processing time
- Failed payment rate
- Webhook delivery success rate
- Revenue by day/week/month
- Customer retry patterns
```

---

## 🧪 TESTING APPROACH

### Unit Tests
```python
def test_mtn_gateway_initiate():
    payment = create_test_payment(method='mtn_mobile_money')
    gateway = MTNMobileMoneyGateway()
    result = gateway.initiate_payment(payment)
    assert result['success'] == True
    assert 'transaction_id' in result

def test_webhook_signature_verification():
    webhook_data = {...}
    signature = generate_webhook_signature(webhook_data)
    assert verify_signature(signature, webhook_data) == True
```

### Integration Tests
```python
def test_complete_payment_flow():
    # 1. Create order
    order = Order.objects.create(...)
    
    # 2. Create payment
    payment = Payment.objects.create(order=order, ...)
    
    # 3. Initiate payment
    gateway = PaymentGatewayService.get_gateway(payment.payment_method)
    result = gateway.initiate_payment(payment)
    
    # 4. Simulate webhook callback
    webhook_payload = {...}
    process_webhook(webhook_payload)
    
    # 5. Verify payment completed
    payment.refresh_from_db()
    assert payment.status == 'COMPLETED'
    assert order.is_paid == True
```

---

## 🚨 ERROR HANDLING

### Gateway Connection Error
```python
try:
    result = gateway.initiate_payment(payment)
except requests.ConnectionError:
    logger.error("Cannot reach payment gateway")
    payment.status = 'FAILED'
    payment.error_message = 'Gateway connection failed'
    return {'success': False, 'error': 'Payment service temporarily unavailable'}
```

### Invalid Credentials Error
```python
try:
    token = gateway._get_access_token()
except AuthenticationError:
    logger.error("Invalid gateway credentials")
    return {'success': False, 'error': 'Payment configuration error'}
```

### Webhook Signature Mismatch
```python
def verify_webhook(signature, data):
    try:
        if not verify_signature(signature, data):
            logger.warning("Webhook signature mismatch - possible tampering")
            return {'success': False, 'error': 'Invalid signature'}
        return process_webhook(data)
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        return {'success': False, 'error': 'Processing error'}
```

---

## 🔄 TRANSACTION STATES

```
┌──────────────────────────────────────────────────────────┐
│                 Payment Life Cycle                        │
└──────────────────────────────────────────────────────────┘

   CREATED
      ↓
   PENDING ──────→ (Waiting for gateway response)
      ↓
   PROCESSING ──→ (Gateway processing/verifying)
      ↓
   ┌─ COMPLETED (Payment successful) ✅
   │
   ├─ FAILED (Payment failed) ❌
   │
   ├─ CANCELLED (User cancelled) ⏹️
   │
   └─ REFUNDED (Payment refunded) 🔄

Webhook received → Update status
Manual verification → Update status
User cancels → CANCELLED status
Refund requested → REFUNDED status
```

---

## 📞 PRODUCTION SUPPORT

### Daily Checklist
- [ ] All payment gateways responding normally
- [ ] No failed payments in past hour
- [ ] Webhook delivery success rate > 99%
- [ ] No pending payments older than 1 hour

### Weekly Checklist
- [ ] Review payment metrics
- [ ] Check for gateway updates
- [ ] Review and resolve failed payments
- [ ] Verify backup completion

### Monthly Checklist
- [ ] Reconcile payments with gateway reports
- [ ] Review security settings
- [ ] Update documentation
- [ ] Plan for API updates

---

## 📚 RELATED DOCUMENTS

- [PAYMENT_FINALIZATION_CHECKLIST.md](PAYMENT_FINALIZATION_CHECKLIST.md) - Implementation checklist
- [PAYMENT_SETUP_GUIDE.md](PAYMENT_SETUP_GUIDE.md) - Quick setup instructions
- [PAYMENT_GATEWAY_INTEGRATION.md](PAYMENT_GATEWAY_INTEGRATION.md) - Full integration guide
- [PAYMENT_GATEWAY_INTEGRATION_SUMMARY.md](PAYMENT_GATEWAY_INTEGRATION_SUMMARY.md) - Features overview

---

**Version**: 1.0  
**Last Updated**: February 1, 2026  
**Status**: Production Ready ✅
