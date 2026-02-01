"""
Order calculation service for smart pricing with discounts
"""

from decimal import Decimal
from django.db.models import Sum
from subscriptions.models import VIPTier, LoyaltyPoints, ReferralProgram
from corporate.models import CorporateEmployee, CorporateContract

class OrderCalculationService:
    """Service for calculating order totals with all discounts applied"""
    
    @staticmethod
    def calculate_order_total(cart, user, loyalty_points_to_redeem=0):
        """
        Calculate order total with all applicable discounts.
        """
        
        # Calculate subtotal from cart
        subtotal = cart.get_total()
        
        # Initialize discount tracking
        vip_discount_amount = Decimal('0.00')
        vip_discount_percent = 0
        corporate_discount_amount = Decimal('0.00')
        corporate_discount_percent = 0
        loyalty_discount_amount = Decimal('0.00')
        referral_discount_amount = Decimal('0.00')
        referral_discount_percent = 0
        
        # 1. VIP Tier Discount
        try:
            vip_tier = VIPTier.objects.get(user=user)
            benefits = vip_tier.get_benefits()
            vip_discount_percent = benefits.get('discount', 0)
            
            if vip_discount_percent > 0:
                vip_discount_amount = subtotal * (Decimal(str(vip_discount_percent)) / 100)
        except VIPTier.DoesNotExist:
            pass
            
        # 2. Corporate Discount
        try:
            employee = CorporateEmployee.objects.get(user=user, is_active=True)
            contract = CorporateContract.objects.filter(
                partner=employee.partner, 
                is_active=True
            ).first()
            
            if contract:
                corporate_discount_percent = float(contract.discount_percentage)
                corporate_discount_amount = subtotal * (Decimal(str(corporate_discount_percent)) / 100)
        except Exception:
            # Catching all exceptions (including OperationalError if table is missing)
            pass
        
        # 3. Referral Discount (10% off first order)
        try:
            referral = ReferralProgram.objects.filter(
                referee=user,
                status='PENDING'
            ).first()
            
            if referral:
                referral_discount_percent = float(referral.referee_discount_percent)
                referral_discount_amount = subtotal * (Decimal(str(referral_discount_percent)) / 100)
        except ReferralProgram.DoesNotExist:
            pass
        
        # 4. Loyalty Points Redemption
        if loyalty_points_to_redeem > 0:
            try:
                loyalty_points = LoyaltyPoints.objects.get(user=user)
                if loyalty_points.balance >= loyalty_points_to_redeem:
                    loyalty_discount_amount = Decimal(loyalty_points_to_redeem * 100)
            except LoyaltyPoints.DoesNotExist:
                pass
        
        # Calculate total discount
        # Policy: Take the highest of VIP or Corporate discount, then add others
        if corporate_discount_amount > vip_discount_amount:
            base_discount_amount = corporate_discount_amount
            vip_discount_amount = Decimal('0.00') # Reset VIP if corporate is better
        else:
            base_discount_amount = vip_discount_amount
            corporate_discount_amount = Decimal('0.00') # Reset corporate if VIP is better
            
        total_discount = base_discount_amount + loyalty_discount_amount + referral_discount_amount
        
        # Calculate subtotal after discounts
        subtotal_after_discounts = subtotal - total_discount
        
        if subtotal_after_discounts < 0:
            subtotal_after_discounts = Decimal('0.00')
            total_discount = subtotal
        
        delivery_charge = Decimal('0.00')
        grand_total = subtotal_after_discounts + delivery_charge
        
        return {
            'subtotal': subtotal,
            'vip_discount_amount': vip_discount_amount,
            'vip_discount_percent': vip_discount_percent,
            'corporate_discount_amount': corporate_discount_amount,
            'corporate_discount_percent': corporate_discount_percent,
            'loyalty_points_redeemed': loyalty_points_to_redeem,
            'loyalty_discount_amount': loyalty_discount_amount,
            'referral_discount_amount': referral_discount_amount,
            'referral_discount_percent': referral_discount_percent,
            'total_discount': total_discount,
            'delivery_charge': delivery_charge,
            'grand_total': grand_total,
        }
    
    @staticmethod
    def get_user_loyalty_info(user):
        """Get user's VIP tier, corporate and loyalty points info"""
        
        info = {
            'vip_tier': None,
            'vip_tier_name': 'None',
            'vip_discount': 0,
            'corporate_partner': None,
            'corporate_discount': 0,
            'loyalty_balance': 0,
            'loyalty_value_rwf': 0,
            'has_referral_discount': False,
            'referral_discount_percent': 0,
        }
        
        # VIP Tier
        try:
            vip_tier = VIPTier.objects.get(user=user)
            benefits = vip_tier.get_benefits()
            info['vip_tier'] = vip_tier
            info['vip_tier_name'] = vip_tier.get_tier_level_display()
            info['vip_discount'] = benefits.get('discount', 0)
        except VIPTier.DoesNotExist:
            pass
            
        # Corporate Info
        try:
            employee = CorporateEmployee.objects.get(user=user, is_active=True)
            contract = CorporateContract.objects.filter(
                partner=employee.partner, 
                is_active=True
            ).first()
            
            info['corporate_partner'] = employee.partner.name
            if contract:
                info['corporate_discount'] = float(contract.discount_percentage)
        except Exception:
            # Catching all exceptions (including OperationalError if table is missing)
            pass
        
        # Loyalty Points
        try:
            loyalty_points = LoyaltyPoints.objects.get(user=user)
            info['loyalty_balance'] = loyalty_points.balance
            info['loyalty_value_rwf'] = loyalty_points.value_in_rwf
        except LoyaltyPoints.DoesNotExist:
            pass
        
        # Referral Discount
        try:
            referral = ReferralProgram.objects.filter(
                referee=user,
                status='PENDING'
            ).first()
            
            if referral:
                info['has_referral_discount'] = True
                info['referral_discount_percent'] = float(referral.referee_discount_percent)
        except:
            pass
        
        return info
