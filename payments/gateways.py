"""
Payment Gateway Integration Service
Supports multiple payment methods with real API integrations
Hospital-ready payment processing system
"""

import requests
import json
import logging
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from .models import Payment, PaymentStatus, PaymentMethod

logger = logging.getLogger(__name__)


class PaymentGatewayError(Exception):
    """Custom exception for payment gateway errors"""
    pass


class BasePaymentGateway:
    """Base class for payment gateways"""
    
    def __init__(self):
        self.api_key = None
        self.api_secret = None
        self.environment = getattr(settings, 'PAYMENT_ENVIRONMENT', 'sandbox')
    
    def initiate_payment(self, payment: Payment, **kwargs):
        """Initiate payment with the gateway"""
        raise NotImplementedError("Subclasses must implement initiate_payment")
    
    def verify_payment(self, payment: Payment, transaction_id: str):
        """Verify payment status with the gateway"""
        raise NotImplementedError("Subclasses must implement verify_payment")
    
    def process_webhook(self, payload: dict):
        """Process webhook callback from gateway"""
        raise NotImplementedError("Subclasses must implement process_webhook")


class MTNMobileMoneyGateway(BasePaymentGateway):
    """MTN Mobile Money Payment Gateway"""
    
    def __init__(self):
        super().__init__()
        self.api_key = getattr(settings, 'MTN_MOMO_API_KEY', '')
        self.api_secret = getattr(settings, 'MTN_MOMO_API_SECRET', '')
        self.subscription_key = getattr(settings, 'MTN_MOMO_SUBSCRIPTION_KEY', '')
        self.environment = getattr(settings, 'PAYMENT_ENVIRONMENT', 'sandbox')
        
        if self.environment == 'sandbox':
            self.base_url = 'https://sandbox.momodeveloper.mtn.com'
        else:
            self.base_url = 'https://api.momodeveloper.mtn.com'
    
    def initiate_payment(self, payment: Payment, **kwargs):
        """Initiate MTN Mobile Money payment"""
        try:
            phone_number = kwargs.get('phone_number', payment.phone_number)
            if not phone_number:
                raise PaymentGatewayError("Phone number is required for MTN Mobile Money")
            
            # Get access token
            token = self._get_access_token()
            
            # Prepare payment request
            payment_request = {
                "amount": str(payment.amount),
                "currency": getattr(settings, 'CURRENCY_CODE', 'UGX'),
                "externalId": f"ORDER_{payment.order.order_number}",
                "payer": {
                    "partyIdType": "MSISDN",
                    "partyId": phone_number.replace('+', '').replace(' ', '')
                },
                "payerMessage": f"Payment for order {payment.order.order_number}",
                "payeeNote": f"Order {payment.order.order_number} - Hospital Meal Service"
            }
            
            # Make API request
            headers = {
                'Authorization': f'Bearer {token}',
                'X-Target-Environment': self.environment,
                'Content-Type': 'application/json',
                'X-Reference-Id': str(payment.id),
                'Ocp-Apim-Subscription-Key': self.subscription_key
            }
            
            response = requests.post(
                f'{self.base_url}/collection/v1_0/requesttopay',
                json=payment_request,
                headers=headers,
                timeout=30
            )
            
            if response.status_code in [200, 202]:
                transaction_id = response.headers.get('X-Reference-Id', str(payment.id))
                payment.transaction_id = transaction_id
                payment.status = PaymentStatus.PROCESSING
                payment.save()
                
                return {
                    'success': True,
                    'transaction_id': transaction_id,
                    'status': 'processing',
                    'message': 'Payment request sent. Please approve on your phone.'
                }
            else:
                error_data = response.json() if response.content else {}
                raise PaymentGatewayError(
                    f"MTN Mobile Money API error: {error_data.get('message', response.text)}"
                )
                
        except requests.RequestException as e:
            logger.error(f"MTN Mobile Money API request failed: {str(e)}")
            raise PaymentGatewayError(f"Failed to initiate payment: {str(e)}")
        except Exception as e:
            logger.error(f"MTN Mobile Money payment error: {str(e)}")
            raise PaymentGatewayError(f"Payment initiation failed: {str(e)}")
    
    def verify_payment(self, payment: Payment, transaction_id: str = None):
        """Verify MTN Mobile Money payment status"""
        try:
            transaction_id = transaction_id or payment.transaction_id
            if not transaction_id:
                raise PaymentGatewayError("Transaction ID is required")
            
            token = self._get_access_token()
            headers = {
                'Authorization': f'Bearer {token}',
                'X-Target-Environment': self.environment,
                'Ocp-Apim-Subscription-Key': self.subscription_key
            }
            
            response = requests.get(
                f'{self.base_url}/collection/v1_0/requesttopay/{transaction_id}',
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', '').upper()
                
                if status == 'SUCCESSFUL':
                    payment.status = PaymentStatus.COMPLETED
                    payment.paid_at = timezone.now()
                    payment.save()
                    return {'success': True, 'status': 'completed'}
                elif status == 'FAILED':
                    payment.status = PaymentStatus.FAILED
                    payment.save()
                    return {'success': False, 'status': 'failed'}
                else:
                    return {'success': True, 'status': 'processing'}
            else:
                return {'success': False, 'status': 'unknown'}
                
        except Exception as e:
            logger.error(f"MTN Mobile Money verification error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _get_access_token(self):
        """Get OAuth access token from MTN API"""
        try:
            auth_url = f'{self.base_url}/collection/token/'
            headers = {
                'Authorization': f'Basic {self._get_basic_auth()}',
                'Ocp-Apim-Subscription-Key': self.subscription_key
            }
            
            response = requests.post(auth_url, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.json().get('access_token')
            else:
                raise PaymentGatewayError("Failed to get access token")
        except Exception as e:
            logger.error(f"MTN token error: {str(e)}")
            raise PaymentGatewayError(f"Authentication failed: {str(e)}")
    
    def _get_basic_auth(self):
        """Generate basic auth string"""
        import base64
        auth_string = f"{self.api_key}:{self.api_secret}"
        return base64.b64encode(auth_string.encode()).decode()


class AirtelMoneyGateway(BasePaymentGateway):
    """Airtel Money Payment Gateway"""
    
    def __init__(self):
        super().__init__()
        self.client_id = getattr(settings, 'AIRTEL_MONEY_CLIENT_ID', '')
        self.client_secret = getattr(settings, 'AIRTEL_MONEY_CLIENT_SECRET', '')
        self.environment = getattr(settings, 'PAYMENT_ENVIRONMENT', 'sandbox')
        
        if self.environment == 'sandbox':
            self.base_url = 'https://openapiuat.airtel.africa'
        else:
            self.base_url = 'https://openapi.airtel.africa'
    
    def initiate_payment(self, payment: Payment, **kwargs):
        """Initiate Airtel Money payment"""
        try:
            phone_number = kwargs.get('phone_number', payment.phone_number)
            if not phone_number:
                raise PaymentGatewayError("Phone number is required for Airtel Money")
            
            # Get access token
            token = self._get_access_token()
            
            # Prepare payment request
            payment_request = {
                "payee": {
                    "msisdn": phone_number.replace('+', '').replace(' ', '')
                },
                "reference": f"ORDER_{payment.order.order_number}",
                "pin": "",  # Customer will enter PIN on their phone
                "transaction": {
                    "amount": str(payment.amount),
                    "id": f"TXN_{payment.id}"
                }
            }
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'X-Country': getattr(settings, 'COUNTRY_CODE', 'UG'),
                'X-Currency': getattr(settings, 'CURRENCY_CODE', 'UGX')
            }
            
            response = requests.post(
                f'{self.base_url}/merchant/v1/payments',
                json=payment_request,
                headers=headers,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                transaction_id = data.get('data', {}).get('transaction', {}).get('id', str(payment.id))
                payment.transaction_id = transaction_id
                payment.status = PaymentStatus.PROCESSING
                payment.save()
                
                return {
                    'success': True,
                    'transaction_id': transaction_id,
                    'status': 'processing',
                    'message': 'Payment request sent. Please approve on your phone.'
                }
            else:
                error_data = response.json() if response.content else {}
                raise PaymentGatewayError(
                    f"Airtel Money API error: {error_data.get('message', response.text)}"
                )
                
        except requests.RequestException as e:
            logger.error(f"Airtel Money API request failed: {str(e)}")
            raise PaymentGatewayError(f"Failed to initiate payment: {str(e)}")
        except Exception as e:
            logger.error(f"Airtel Money payment error: {str(e)}")
            raise PaymentGatewayError(f"Payment initiation failed: {str(e)}")
    
    def verify_payment(self, payment: Payment, transaction_id: str = None):
        """Verify Airtel Money payment status"""
        try:
            transaction_id = transaction_id or payment.transaction_id
            if not transaction_id:
                raise PaymentGatewayError("Transaction ID is required")
            
            token = self._get_access_token()
            headers = {
                'Authorization': f'Bearer {token}',
                'X-Country': getattr(settings, 'COUNTRY_CODE', 'UG'),
                'X-Currency': getattr(settings, 'CURRENCY_CODE', 'UGX')
            }
            
            response = requests.get(
                f'{self.base_url}/standard/v1/payments/{transaction_id}',
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', {}).get('status', '').upper()
                
                if status == 'TS':
                    payment.status = PaymentStatus.COMPLETED
                    payment.paid_at = timezone.now()
                    payment.save()
                    return {'success': True, 'status': 'completed'}
                elif status == 'TF':
                    payment.status = PaymentStatus.FAILED
                    payment.save()
                    return {'success': False, 'status': 'failed'}
                else:
                    return {'success': True, 'status': 'processing'}
            else:
                return {'success': False, 'status': 'unknown'}
                
        except Exception as e:
            logger.error(f"Airtel Money verification error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _get_access_token(self):
        """Get OAuth access token from Airtel API"""
        try:
            auth_url = f'{self.base_url}/auth/oauth2/token'
            headers = {
                'Content-Type': 'application/json'
            }
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'client_credentials'
            }
            
            response = requests.post(auth_url, json=data, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.json().get('access_token')
            else:
                raise PaymentGatewayError("Failed to get access token")
        except Exception as e:
            logger.error(f"Airtel token error: {str(e)}")
            raise PaymentGatewayError(f"Authentication failed: {str(e)}")


class FlutterwaveGateway(BasePaymentGateway):
    """Flutterwave Payment Gateway (for Bank Transfer and Card Payments)"""
    
    def __init__(self):
        super().__init__()
        self.public_key = getattr(settings, 'FLUTTERWAVE_PUBLIC_KEY', '')
        self.secret_key = getattr(settings, 'FLUTTERWAVE_SECRET_KEY', '')
        self.environment = getattr(settings, 'PAYMENT_ENVIRONMENT', 'sandbox')
        
        if self.environment == 'sandbox':
            self.base_url = 'https://api.flutterwave.com/v3'
        else:
            self.base_url = 'https://api.flutterwave.com/v3'
    
    def initiate_payment(self, payment: Payment, **kwargs):
        """Initiate Flutterwave payment (Bank Transfer or Card)"""
        try:
            payment_method = kwargs.get('payment_type', 'bank_transfer')
            
            # Prepare payment request
            payment_data = {
                "tx_ref": f"ORDER_{payment.order.order_number}_{payment.id}",
                "amount": float(payment.amount),
                "currency": getattr(settings, 'CURRENCY_CODE', 'UGX'),
                "redirect_url": f"{settings.SITE_URL}/payments/callback/",
                "customer": {
                    "email": payment.order.user.email,
                    "name": payment.order.user.get_full_name() or payment.order.user.username,
                    "phone_number": payment.phone_number or ""
                },
                "customizations": {
                    "title": "Hospital Meal Service Payment",
                    "description": f"Payment for order {payment.order.order_number}",
                    "logo": getattr(settings, 'PAYMENT_LOGO_URL', '')
                },
                "meta": {
                    "order_number": payment.order.order_number,
                    "payment_id": payment.id
                }
            }
            
            # Add payment method specific data
            if payment_method == 'card':
                payment_data["payment_options"] = "card"
            elif payment_method == 'bank_transfer':
                payment_data["payment_options"] = "banktransfer"
                payment_data["bank_transfer_options"] = {
                    "account_number": kwargs.get('account_number', payment.account_number)
                }
            
            headers = {
                'Authorization': f'Bearer {self.secret_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f'{self.base_url}/payments',
                json=payment_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    payment_link = data.get('data', {}).get('link')
                    transaction_id = data.get('data', {}).get('tx_ref', f"FLW_{payment.id}")
                    
                    payment.transaction_id = transaction_id
                    payment.status = PaymentStatus.PROCESSING
                    payment.save()
                    
                    return {
                        'success': True,
                        'transaction_id': transaction_id,
                        'payment_link': payment_link,
                        'status': 'processing',
                        'message': 'Redirect to payment page'
                    }
                else:
                    raise PaymentGatewayError(data.get('message', 'Payment initiation failed'))
            else:
                error_data = response.json() if response.content else {}
                raise PaymentGatewayError(
                    f"Flutterwave API error: {error_data.get('message', response.text)}"
                )
                
        except requests.RequestException as e:
            logger.error(f"Flutterwave API request failed: {str(e)}")
            raise PaymentGatewayError(f"Failed to initiate payment: {str(e)}")
        except Exception as e:
            logger.error(f"Flutterwave payment error: {str(e)}")
            raise PaymentGatewayError(f"Payment initiation failed: {str(e)}")
    
    def verify_payment(self, payment: Payment, transaction_id: str = None):
        """Verify Flutterwave payment status"""
        try:
            transaction_id = transaction_id or payment.transaction_id
            if not transaction_id:
                raise PaymentGatewayError("Transaction ID is required")
            
            headers = {
                'Authorization': f'Bearer {self.secret_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f'{self.base_url}/transactions/{transaction_id}/verify',
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', '')
                transaction_data = data.get('data', {})
                
                if status == 'success' and transaction_data.get('status') == 'successful':
                    payment.status = PaymentStatus.COMPLETED
                    payment.paid_at = timezone.now()
                    payment.transaction_id = transaction_data.get('tx_ref', transaction_id)
                    payment.save()
                    return {'success': True, 'status': 'completed'}
                elif transaction_data.get('status') == 'failed':
                    payment.status = PaymentStatus.FAILED
                    payment.save()
                    return {'success': False, 'status': 'failed'}
                else:
                    return {'success': True, 'status': 'processing'}
            else:
                return {'success': False, 'status': 'unknown'}
                
        except Exception as e:
            logger.error(f"Flutterwave verification error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def process_webhook(self, payload: dict):
        """Process Flutterwave webhook"""
        try:
            import hashlib
            import hmac
            
            # Verify webhook signature
            secret_hash = getattr(settings, 'FLUTTERWAVE_SECRET_HASH', '')
            if secret_hash:
                signature = payload.get('signature', '')
                computed_hash = hmac.new(
                    secret_hash.encode(),
                    json.dumps(payload).encode(),
                    hashlib.sha256
                ).hexdigest()
                
                if signature != computed_hash:
                    raise PaymentGatewayError("Invalid webhook signature")
            
            event = payload.get('event', '')
            data = payload.get('data', {})
            
            if event == 'charge.completed':
                transaction_ref = data.get('tx_ref', '')
                if transaction_ref.startswith('ORDER_'):
                    # Extract payment ID from transaction ref
                    parts = transaction_ref.split('_')
                    if len(parts) >= 3:
                        payment_id = parts[-1]
                        try:
                            payment = Payment.objects.get(id=payment_id)
                            if data.get('status') == 'successful':
                                payment.status = PaymentStatus.COMPLETED
                                payment.paid_at = timezone.now()
                                payment.transaction_id = transaction_ref
                                payment.save()
                                return {'success': True, 'payment_id': payment_id}
                        except Payment.DoesNotExist:
                            logger.warning(f"Payment not found: {payment_id}")
            
            return {'success': False, 'message': 'Event not processed'}
            
        except Exception as e:
            logger.error(f"Flutterwave webhook error: {str(e)}")
            raise PaymentGatewayError(f"Webhook processing failed: {str(e)}")


class PaymentGatewayService:
    """Main payment gateway service that routes to appropriate gateway"""
    
    @staticmethod
    def get_gateway(payment_method: str) -> BasePaymentGateway:
        """Get appropriate payment gateway for payment method"""
        if payment_method == PaymentMethod.MTN_MOBILE_MONEY:
            return MTNMobileMoneyGateway()
        elif payment_method == PaymentMethod.AIRTEL_MONEY:
            return AirtelMoneyGateway()
        elif payment_method in [PaymentMethod.BANK_TRANSFER, PaymentMethod.CARD]:
            return FlutterwaveGateway()
        else:
            raise PaymentGatewayError(f"Unsupported payment method: {payment_method}")
    
    @staticmethod
    def initiate_payment(payment: Payment, **kwargs):
        """Initiate payment using appropriate gateway"""
        gateway = PaymentGatewayService.get_gateway(payment.payment_method)
        
        # Add payment type for Flutterwave
        if payment.payment_method == PaymentMethod.BANK_TRANSFER:
            kwargs['payment_type'] = 'bank_transfer'
        elif payment.payment_method == PaymentMethod.CARD:
            kwargs['payment_type'] = 'card'
        
        return gateway.initiate_payment(payment, **kwargs)
    
    @staticmethod
    def verify_payment(payment: Payment, transaction_id: str = None):
        """Verify payment status using appropriate gateway"""
        gateway = PaymentGatewayService.get_gateway(payment.payment_method)
        return gateway.verify_payment(payment, transaction_id)
    
    @staticmethod
    def process_webhook(payment_method: str, payload: dict):
        """Process webhook from payment gateway"""
        gateway = PaymentGatewayService.get_gateway(payment_method)
        return gateway.process_webhook(payload)
