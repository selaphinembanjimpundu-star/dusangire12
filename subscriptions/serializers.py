from rest_framework import serializers
from .models import (
    VIPTier, LoyaltyPoints, LoyaltyTransaction, ReferralProgram,
    SubscriptionAutoRenewal, Subscription
)

class VIPTierSerializer(serializers.ModelSerializer):
    """Serializer for VIP Tier status"""
    tier_display = serializers.CharField(source='get_tier_level_display', read_only=True)
    next_tier_progress = serializers.SerializerMethodField()
    benefits = serializers.SerializerMethodField()
    
    class Meta:
        model = VIPTier
        fields = [
            'tier_level', 'tier_display', 'spending_ytd', 'spending_total',
            'promotion_percentage', 'next_tier_threshold', 'achieved_at',
            'next_tier_progress', 'benefits'
        ]
        
    def get_next_tier_progress(self, obj):
        """Calculate percentage progress to next tier"""
        if obj.next_tier_threshold > 0:
            return min(100, int((obj.spending_total / obj.next_tier_threshold) * 100))
        return 100
        
    def get_benefits(self, obj):
        return obj.get_benefits()


class LoyaltyPointsSerializer(serializers.ModelSerializer):
    """Serializer for Loyalty Points balance"""
    value_in_rwf = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = LoyaltyPoints
        fields = [
            'balance', 'earned_total', 'redeemed_total', 
            'subscription_bonus_rate', 'value_in_rwf', 'expires_at'
        ]


class LoyaltyTransactionSerializer(serializers.ModelSerializer):
    """Serializer for Loyalty Transactions"""
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    
    class Meta:
        model = LoyaltyTransaction
        fields = [
            'transaction_type', 'transaction_type_display', 'points_amount',
            'description', 'balance_before', 'balance_after', 'created_at'
        ]


class ReferralProgramSerializer(serializers.ModelSerializer):
    """Serializer for Referral Program info"""
    referral_link = serializers.SerializerMethodField()
    
    class Meta:
        model = ReferralProgram
        fields = [
            'referral_code', 'referral_link', 'referrer_bonus_rwf',
            'referrer_bonus_points', 'referee_discount_percent'
        ]
        
    def get_referral_link(self, obj):
        if not obj.referral_link:
            return obj.generate_referral_link()
        return obj.referral_link


class SubscriptionAutoRenewalSerializer(serializers.ModelSerializer):
    """Serializer for Auto-Renewal settings"""
    subscription_plan = serializers.CharField(source='subscription.plan.name', read_only=True)
    
    class Meta:
        model = SubscriptionAutoRenewal
        fields = [
            'subscription_plan', 'auto_renew_enabled', 'renewal_date',
            'payment_method_id', 'last_renewal_status', 'next_retry_at'
        ]
        read_only_fields = ['renewal_date', 'last_renewal_status', 'next_retry_at']
