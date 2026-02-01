from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import (
    VIPTier, LoyaltyPoints, LoyaltyTransaction, ReferralProgram,
    SubscriptionAutoRenewal, Subscription
)
from .serializers import (
    VIPTierSerializer, LoyaltyPointsSerializer, 
    LoyaltyTransactionSerializer, ReferralProgramSerializer,
    SubscriptionAutoRenewalSerializer
)
from .services import LoyaltyService

class LoyaltyStatusView(APIView):
    """Get user's loyalty status (Points + VIP Tier)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Ensure records exist
        vip_tier = LoyaltyService.calculate_vip_tier(user)
        loyalty_points, _ = LoyaltyPoints.objects.get_or_create(user=user)
        
        return Response({
            'vip_tier': VIPTierSerializer(vip_tier).data,
            'points': LoyaltyPointsSerializer(loyalty_points).data
        })


class LoyaltyHistoryView(APIView):
    """Get user's loyalty transaction history"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        transactions = LoyaltyTransaction.objects.filter(user=request.user)
        serializer = LoyaltyTransactionSerializer(transactions, many=True)
        return Response(serializer.data)


class RedeemPointsView(APIView):
    """Redeem loyalty points"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        points_to_redeem = request.data.get('points')
        
        if not points_to_redeem:
            return Response({'error': 'Points amount required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            points_to_redeem = int(points_to_redeem)
            if points_to_redeem < 100:
                return Response({'error': 'Minimum redemption is 100 points'}, status=status.HTTP_400_BAD_REQUEST)
                
            loyalty_points = LoyaltyPoints.objects.get(user=request.user)
            
            if loyalty_points.balance < points_to_redeem:
                return Response({'error': 'Insufficient points'}, status=status.HTTP_400_BAD_REQUEST)
                
            # Perform redemption
            loyalty_points.redeem_points(points_to_redeem, "User redemption via API")
            
            # Here you would typically add credits to user's wallet or generate a coupon
            # For now, we just return success
            
            return Response({
                'success': True,
                'message': f'Redeemed {points_to_redeem} points',
                'new_balance': loyalty_points.balance,
                'credit_value': points_to_redeem * 100  # 1 pt = 100 RWF
            })
            
        except ValueError:
            return Response({'error': 'Invalid points amount'}, status=status.HTTP_400_BAD_REQUEST)
        except LoyaltyPoints.DoesNotExist:
            return Response({'error': 'Loyalty account not found'}, status=status.HTTP_404_NOT_FOUND)


class ReferralInfoView(APIView):
    """Get user's referral information"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Get or create referral program entry for this user (as referrer)
        # Note: The model structure assumes one ReferralProgram entry per referral relationship
        # But we need a "Referrer Profile" concept. 
        # For now, we'll check if they have any referrals or create a dummy one to generate code
        
        # Wait, the ReferralProgram model is per-referral (referrer -> referee).
        # We need a way to store the user's PERMANENT referral code.
        # Looking at signals.py, it seems we generate code on ReferralProgram creation.
        # But usually a user has ONE code they share with everyone.
        # Let's check the model again.
        
        # Model: ReferralProgram has 'referral_code' unique=True.
        # This implies each ReferralProgram instance has a unique code? 
        # Or does the user have a unique code?
        # If ReferralProgram is "User A invited User B", then the code should be User A's code.
        # If the code is unique per ReferralProgram, then it's a unique link per invite.
        
        # Let's assume for this API we want to give the user a code to share.
        # If the system is "unique link per invite", we should generate a new one.
        # If it's "user has a code", we need to find it.
        
        # Let's create a generic "invite" for the user if none exists to get a code.
        # Or better, let's just generate a code for them if they don't have one in any 'PENDING' referral?
        # Actually, usually 'referral_code' is on the UserProfile or a separate Referrer model.
        # In this schema, ReferralProgram seems to be the "Invite".
        
        # Let's implement "Generate New Invite Link" behavior.
        
        referral = ReferralProgram.objects.create(
            referrer=request.user,
            status='PENDING'
        )
        # Signal will generate code
        
        return Response(ReferralProgramSerializer(referral).data)


class AutoRenewalView(APIView):
    """Manage auto-renewal for a subscription"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, subscription_id):
        subscription = get_object_or_404(Subscription, id=subscription_id, user=request.user)
        try:
            auto_renewal = subscription.auto_renewal
            return Response(SubscriptionAutoRenewalSerializer(auto_renewal).data)
        except SubscriptionAutoRenewal.DoesNotExist:
            return Response({'error': 'Auto-renewal not configured'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, subscription_id):
        subscription = get_object_or_404(Subscription, id=subscription_id, user=request.user)
        enabled = request.data.get('enabled')
        
        if enabled is None:
            return Response({'error': 'Enabled status required'}, status=status.HTTP_400_BAD_REQUEST)
            
        auto_renewal, _ = SubscriptionAutoRenewal.objects.get_or_create(
            subscription=subscription,
            defaults={'renewal_date': subscription.end_date}
        )
        
        auto_renewal.auto_renew_enabled = bool(enabled)
        if request.data.get('payment_method_id'):
            auto_renewal.payment_method_id = request.data.get('payment_method_id')
            
        auto_renewal.save()
        
        # Also update subscription model for consistency
        subscription.auto_renewal_enabled = bool(enabled)
        subscription.save()
        
        return Response(SubscriptionAutoRenewalSerializer(auto_renewal).data)
