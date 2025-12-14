# Payment Gateway Integration - Hospital Ready

## Overview

This document describes the comprehensive payment gateway integration system that supports all payment methods with real API integrations. The system is designed to be hospital-ready and can be easily acquired and configured by hospitals.

## Supported Payment Methods

### 1. MTN Mobile Money
- **Gateway**: MTN Mobile Money API
- **Integration**: Full API integration with webhook support
- **Features**: 
  - Real-time payment initiation
  - Automatic payment verification
  - Webhook callbacks for payment status updates

### 2. Airtel Money
- **Gateway**: Airtel Money API
- **Integration**: Full API integration with webhook support
- **Features**:
  - Real-time payment initiation
  - Automatic payment verification
  - Webhook callbacks for payment status updates

### 3. Bank Transfer
- **Gateway**: Flutterwave
- **Integration**: Full API integration with redirect-based payment
- **Features**:
  - Secure bank transfer processing
  - Payment link generation
  - Automatic verification

### 4. Card Payment
- **Gateway**: Flutterwave
- **Integration**: Full API integration with redirect-based payment
- **Features**:
  - Secure card payment processing
  - Payment link generation
  - Support for multiple card types

### 5. Cash on Delivery
- **Gateway**: None (manual processing)
- **Integration**: No API required
- **Features**:
  - Order tracking
  - Manual payment confirmation

## Architecture

### Payment Gateway Service (`payments/gateways.py`)

The payment gateway service provides a unified interface for all payment methods:

- **BasePaymentGateway**: Abstract base class for all payment gateways
- **MTNMobileMoneyGateway**: Handles MTN Mobile Money payments
- **AirtelMoneyGateway**: Handles Airtel Money payments
- **FlutterwaveGateway**: Handles bank transfer and card payments
- **PaymentGatewayService**: Main service that routes payments to appropriate gateways

### Webhook Handlers (`payments/webhooks.py`)

Webhook handlers process callbacks from payment gateways:

- **FlutterwaveWebhookView**: Handles Flutterwave webhooks
- **mtn_momo_webhook**: Handles MTN Mobile Money webhooks
- **airtel_money_webhook**: Handles Airtel Money webhooks

### Payment Models

The Payment model has been extended with:

- `gateway_response`: JSON field storing gateway API responses
- `payment_link`: URL field for redirect-based payments
- `gateway_name`: Name of the payment gateway used

## Configuration

### Environment Variables

Add the following to your `.env` file or environment:

```bash
# Payment Environment
PAYMENT_ENVIRONMENT=sandbox  # or 'production'

# Site URL
SITE_URL=https://yourdomain.com

# MTN Mobile Money
MTN_MOMO_API_KEY=your_api_key
MTN_MOMO_API_SECRET=your_api_secret
MTN_MOMO_SUBSCRIPTION_KEY=your_subscription_key

# Airtel Money
AIRTEL_MONEY_CLIENT_ID=your_client_id
AIRTEL_MONEY_CLIENT_SECRET=your_client_secret

# Flutterwave
FLUTTERWAVE_PUBLIC_KEY=your_public_key
FLUTTERWAVE_SECRET_KEY=your_secret_key
FLUTTERWAVE_SECRET_HASH=your_secret_hash

# Currency and Country
CURRENCY_CODE=UGX
COUNTRY_CODE=UG

# Hospital Settings
HOSPITAL_NAME=Your Hospital Name
HOSPITAL_ACQUISITION_MODE=True
```

### Django Settings

The payment gateway settings are configured in `dusangire/settings.py`:

```python
# Payment Gateway Configuration
PAYMENT_ENVIRONMENT = 'sandbox'  # or 'production'
SITE_URL = 'https://yourdomain.com'
CURRENCY_CODE = 'UGX'
COUNTRY_CODE = 'UG'

# Gateway API Keys (set from environment variables)
MTN_MOMO_API_KEY = os.getenv('MTN_MOMO_API_KEY', '')
MTN_MOMO_API_SECRET = os.getenv('MTN_MOMO_API_SECRET', '')
MTN_MOMO_SUBSCRIPTION_KEY = os.getenv('MTN_MOMO_SUBSCRIPTION_KEY', '')

AIRTEL_MONEY_CLIENT_ID = os.getenv('AIRTEL_MONEY_CLIENT_ID', '')
AIRTEL_MONEY_CLIENT_SECRET = os.getenv('AIRTEL_MONEY_CLIENT_SECRET', '')

FLUTTERWAVE_PUBLIC_KEY = os.getenv('FLUTTERWAVE_PUBLIC_KEY', '')
FLUTTERWAVE_SECRET_KEY = os.getenv('FLUTTERWAVE_SECRET_KEY', '')
FLUTTERWAVE_SECRET_HASH = os.getenv('FLUTTERWAVE_SECRET_HASH', '')
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

The `requests` library is required for API calls.

### 2. Run Migrations

```bash
python manage.py makemigrations payments
python manage.py migrate
```

### 3. Configure API Keys

1. **MTN Mobile Money**:
   - Register at [MTN Developer Portal](https://momodeveloper.mtn.com/)
   - Create an app and get API credentials
   - Set up webhook URL: `https://yourdomain.com/payments/webhooks/mtn-momo/`

2. **Airtel Money**:
   - Register at [Airtel Money Developer Portal](https://openapi.airtel.africa/)
   - Create an app and get client credentials
   - Set up webhook URL: `https://yourdomain.com/payments/webhooks/airtel-money/`

3. **Flutterwave**:
   - Register at [Flutterwave Dashboard](https://dashboard.flutterwave.com/)
   - Get API keys from settings
   - Set up webhook URL: `https://yourdomain.com/payments/webhooks/flutterwave/`

### 4. Update Settings

Update `dusangire/settings.py` with your API credentials and site URL.

### 5. Test Payment Flow

1. Create a test order
2. Select a payment method
3. Complete the payment
4. Verify payment status updates

## Payment Flow

### Mobile Money (MTN/Airtel)

1. Customer selects mobile money payment method
2. Customer enters phone number
3. System initiates payment via gateway API
4. Customer receives payment request on phone
5. Customer approves payment
6. Gateway sends webhook callback
7. System verifies and updates payment status

### Bank Transfer / Card Payment

1. Customer selects bank transfer or card payment
2. System initiates payment via Flutterwave
3. Customer is redirected to Flutterwave payment page
4. Customer completes payment
5. Customer is redirected back to confirmation page
6. System verifies payment status
7. Payment is marked as completed

### Cash on Delivery

1. Customer selects cash on delivery
2. Order is created with pending payment
3. Payment is collected upon delivery
4. Admin manually updates payment status

## Webhook Configuration

### MTN Mobile Money Webhook

- **URL**: `https://yourdomain.com/payments/webhooks/mtn-momo/`
- **Method**: POST
- **Authentication**: Configure in MTN Developer Portal

### Airtel Money Webhook

- **URL**: `https://yourdomain.com/payments/webhooks/airtel-money/`
- **Method**: POST
- **Authentication**: Configure in Airtel Developer Portal

### Flutterwave Webhook

- **URL**: `https://yourdomain.com/payments/webhooks/flutterwave/`
- **Method**: POST
- **Authentication**: Secret hash verification

## Hospital Acquisition

### Pre-Acquisition Checklist

1. ✅ All payment methods integrated with real APIs
2. ✅ Webhook handlers configured
3. ✅ Payment verification system in place
4. ✅ Error handling and logging implemented
5. ✅ Security measures (webhook verification, HTTPS)
6. ✅ Documentation complete

### Post-Acquisition Steps

1. **Update Hospital Information**:
   - Update `HOSPITAL_NAME` in settings
   - Update payment page branding
   - Configure hospital-specific payment settings

2. **Configure Production APIs**:
   - Switch `PAYMENT_ENVIRONMENT` to 'production'
   - Update all API keys with production credentials
   - Configure production webhook URLs

3. **Test All Payment Methods**:
   - Test MTN Mobile Money
   - Test Airtel Money
   - Test Bank Transfer
   - Test Card Payment
   - Test Cash on Delivery

4. **Security Review**:
   - Verify webhook signatures
   - Ensure HTTPS is enabled
   - Review API key security
   - Test error handling

5. **Go Live**:
   - Enable production mode
   - Monitor payment transactions
   - Set up alerts for failed payments
   - Configure backup procedures

## API Integration Details

### MTN Mobile Money API

- **Base URL (Sandbox)**: `https://sandbox.momodeveloper.mtn.com`
- **Base URL (Production)**: `https://api.momodeveloper.mtn.com`
- **Authentication**: OAuth 2.0
- **Endpoints**:
  - `/collection/token/` - Get access token
  - `/collection/v1_0/requesttopay` - Initiate payment
  - `/collection/v1_0/requesttopay/{referenceId}` - Check payment status

### Airtel Money API

- **Base URL (Sandbox)**: `https://openapiuat.airtel.africa`
- **Base URL (Production)**: `https://openapi.airtel.africa`
- **Authentication**: OAuth 2.0 Client Credentials
- **Endpoints**:
  - `/auth/oauth2/token` - Get access token
  - `/merchant/v1/payments` - Initiate payment
  - `/standard/v1/payments/{transactionId}` - Check payment status

### Flutterwave API

- **Base URL**: `https://api.flutterwave.com/v3`
- **Authentication**: Bearer token (secret key)
- **Endpoints**:
  - `/payments` - Initiate payment
  - `/transactions/{id}/verify` - Verify payment

## Error Handling

The system includes comprehensive error handling:

- **PaymentGatewayError**: Custom exception for gateway errors
- **Logging**: All errors are logged for debugging
- **User Feedback**: User-friendly error messages
- **Fallback**: Orders are created even if payment initiation fails

## Security Considerations

1. **API Keys**: Store in environment variables, never in code
2. **Webhook Verification**: All webhooks verify signatures
3. **HTTPS**: Required for all payment operations
4. **CSRF Protection**: Enabled for all forms
5. **Input Validation**: All user inputs are validated
6. **Error Messages**: Generic error messages to prevent information leakage

## Testing

### Sandbox Testing

1. Use sandbox API credentials
2. Test with sandbox phone numbers
3. Verify webhook callbacks
4. Test error scenarios

### Production Testing

1. Use production API credentials
2. Test with real payment methods
3. Monitor transaction logs
4. Verify payment confirmations

## Monitoring

### Payment Status Monitoring

- Monitor pending payments
- Track failed payments
- Review processing times
- Check webhook delivery

### Logging

All payment operations are logged:
- Payment initiation
- Gateway responses
- Webhook callbacks
- Error conditions

## Support

For issues or questions:
1. Check logs in Django admin
2. Review payment gateway responses
3. Verify API credentials
4. Test webhook endpoints
5. Contact payment gateway support

## Future Enhancements

- [ ] Payment retry mechanism
- [ ] Automatic refund processing
- [ ] Payment analytics dashboard
- [ ] Multi-currency support
- [ ] Payment method preferences
- [ ] Recurring payment support

## Conclusion

The payment gateway integration is complete and hospital-ready. All payment methods are integrated with real APIs, webhook handlers are configured, and the system is ready for production deployment. The hospital can easily acquire and configure the system by following the setup instructions above.
