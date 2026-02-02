from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import MedicalPrescription, PatientNutritionStatus
from orders.models import Order, Cart, CartItem
from menu.models import DietaryTag


@login_required
def patient_dashboard(request):
    """
    Patient dashboard showing:
    - Current meal plan (prescription)
    - Recent orders
    - Meal compliance metrics
    - Cart status
    - Dietary preferences
    """
    user = request.user
    profile = getattr(user, 'profile', None)
    
    # Get patient's health profile
    health_profile = None
    if profile and hasattr(profile, 'health_profile'):
        health_profile = profile.health_profile
    
    # Get current active meal plan
    meal_plan = None
    has_meal_plan = False
    compliance_percentage = 0
    
    if health_profile:
        meal_plan = MedicalPrescription.objects.filter(
            health_profile=health_profile,
            is_active=True
        ).order_by('-start_date').first()
        
        if meal_plan:
            has_meal_plan = True
            # Calculate compliance percentage
            nutrition_status = PatientNutritionStatus.objects.filter(
                health_profile=health_profile
            ).first()
            if nutrition_status:
                compliance_percentage = int(nutrition_status.meal_compliance_percentage or 0)
    
    # Get recent orders (last 5)
    recent_orders = Order.objects.filter(
        customer=user
    ).select_related('delivery_address').prefetch_related('items').order_by('-created_at')[:5]
    
    # Count orders this month
    first_day_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    orders_this_month = Order.objects.filter(
        customer=user,
        created_at__gte=first_day_of_month
    ).count()
    
    # Get cart count
    cart_count = 0
    try:
        cart = Cart.objects.get(user=user)
        cart_count = CartItem.objects.filter(cart=cart).count()
    except Cart.DoesNotExist:
        cart_count = 0
    
    # Get dietary preferences from user's orders
    dietary_preferences = []
    if health_profile and meal_plan:
        # Add meal plan type as preference
        meal_type_display = meal_plan.get_meal_type_display()
        dietary_preferences.append(meal_type_display)
        
        # Get restrictions if any
        if meal_plan.dietary_restrictions:
            restrictions = meal_plan.dietary_restrictions.split(',')
            dietary_preferences.extend([r.strip() for r in restrictions if r.strip()])
    
    context = {
        'health_profile': health_profile,
        'meal_plan': meal_plan,
        'has_meal_plan': has_meal_plan,
        'compliance_percentage': compliance_percentage,
        'recent_orders': recent_orders,
        'orders_this_month': orders_this_month,
        'cart_count': cart_count,
        'dietary_preferences': dietary_preferences,
    }
    
    return render(request, 'patients/patient_dashboard.html', context)
