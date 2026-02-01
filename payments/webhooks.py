"""
Payment Webhook Handlers
Processes callbacks from payment gateways
"""

import json
import logging
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from .models import Payment, PaymentMethod, PaymentStatus
from .gateways import PaymentGatewayService, PaymentGatewayError

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class FlutterwaveWebhookView(View):
    """Handle Flutterwave webhook callbacks"""
    
    def post(self, request):
        try:
            payload = json.loads(request.body)
            logger.info(f"Flutterwave webhook received: {payload}")
            
            result = PaymentGatewayService.process_webhook(
                PaymentMethod.CARD,  # Flutterwave handles both card and bank transfer
                payload
            )
            
            if result.get('success'):
                return JsonResponse({'status': 'success'}, status=200)
            else:
                return JsonResponse({'status': 'ignored'}, status=200)
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON in Flutterwave webhook")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except PaymentGatewayError as e:
            logger.error(f"Flutterwave webhook error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            logger.error(f"Unexpected webhook error: {str(e)}", exc_info=True)
            return JsonResponse({'error': 'Internal server error'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def mtn_momo_webhook(request):
    """Handle MTN Mobile Money webhook callbacks"""
    try:
        payload = json.loads(request.body)
        logger.info(f"MTN MoMo webhook received: {payload}")
        
        # Extract transaction reference
        transaction_id = payload.get('externalId') or payload.get('financialTransactionId')
        if not transaction_id:
            return JsonResponse({'error': 'Missing transaction ID'}, status=400)
        
        # Find payment by transaction ID
        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
        except Payment.DoesNotExist:
            logger.warning(f"Payment not found for transaction: {transaction_id}")
            return JsonResponse({'error': 'Payment not found'}, status=404)
        
        # Verify payment status
        result = PaymentGatewayService.verify_payment(payment, transaction_id)
        
        if result.get('success'):
            return JsonResponse({'status': 'success'}, status=200)
        else:
            return JsonResponse({'status': 'failed'}, status=200)
            
    except json.JSONDecodeError:
        logger.error("Invalid JSON in MTN MoMo webhook")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"MTN MoMo webhook error: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def airtel_money_webhook(request):
    """Handle Airtel Money webhook callbacks"""
    try:
        payload = json.loads(request.body)
        logger.info(f"Airtel Money webhook received: {payload}")
        
        # Extract transaction ID
        transaction_id = payload.get('transaction', {}).get('id') or payload.get('id')
        if not transaction_id:
            return JsonResponse({'error': 'Missing transaction ID'}, status=400)
        
        # Find payment by transaction ID
        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
        except Payment.DoesNotExist:
            logger.warning(f"Payment not found for transaction: {transaction_id}")
            return JsonResponse({'error': 'Payment not found'}, status=404)
        
        # Verify payment status
        result = PaymentGatewayService.verify_payment(payment, transaction_id)
        
        if result.get('success'):
            return JsonResponse({'status': 'success'}, status=200)
        else:
            return JsonResponse({'status': 'failed'}, status=200)
            
    except json.JSONDecodeError:
        logger.error("Invalid JSON in Airtel Money webhook")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Airtel Money webhook error: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)














