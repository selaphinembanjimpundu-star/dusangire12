from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import MedicalPrescription, PatientNutritionStatus
from orders.models import Order, Cart, CartItem
from menu.models import MenuItem, DietaryTag, Category


@login_required
def patient_portal(request):
    """
    Consolidated patient portal - single unified interface for:
    - Viewing meal plan
    - Browsing & ordering meals
    - Viewing cart
    - Tracking orders
    - Viewing compliance
    """
    user = request.user
    profile = getattr(user, 'profile', None)
    
    # Get patient's health profile
    health_profile = None
    if profile and hasattr(profile, 'health_profile'):
        health_profile = profile.health_profile
    
    # Get current active meal plan
    medical_prescription = None
    compliance_percentage = 0
    prescribed_tag = None
    
    if health_profile:
        medical_prescription = MedicalPrescription.objects.filter(
            health_profile=health_profile,
            is_active=True
        ).order_by('-start_date').first()
        
        if medical_prescription:
            # Calculate compliance percentage
            nutrition_status = PatientNutritionStatus.objects.filter(
                health_profile=health_profile
            ).first()
            if nutrition_status:
                compliance_percentage = int(nutrition_status.meal_compliance_percentage or 0)
            
            # Get prescribed dietary tag for meal filtering
            meal_type_tags = {
                'DIABETIC': 'Diabetic-Friendly',
                'LOW_SODIUM': 'Low-Sodium',
                'HIGH_PROTEIN': 'High-Protein',
                'LOW_FAT': 'Low-Fat',
                'VEGETARIAN': 'Vegetarian',
                'GLUTEN_FREE': 'Gluten-Free',
                'VEGAN': 'Vegan',
            }
            
            tag_name = meal_type_tags.get(medical_prescription.meal_type)
            if tag_name:
                prescribed_tag = DietaryTag.objects.filter(name=tag_name).first()
    
    # Get all available menu items
    menu_items = MenuItem.objects.filter(
        is_available=True
    ).select_related('category').prefetch_related('dietary_tags').order_by('category', 'name')
    
    # Mark meals as allowed/restricted based on prescription
    for item in menu_items:
        if medical_prescription and prescribed_tag:
            item.is_allowed_for_patient = item.dietary_tags.filter(id=prescribed_tag.id).exists()
        else:
            item.is_allowed_for_patient = True
    
    # Get categories for filter
    categories = Category.objects.filter(is_active=True)
    
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
    
    context = {
        'medical_prescription': medical_prescription,
        'menu_items': menu_items,
        'categories': categories,
        'recent_orders': recent_orders,
        'orders_this_month': orders_this_month,
        'cart_count': cart_count,
        'compliance_percentage': compliance_percentage,
        'has_restriction': medical_prescription is not None,
    }
    
    return render(request, 'patients/patient_portal.html', context)


@login_required
def patient_dashboard(request):
    """
    Legacy dashboard - now redirects to unified patient portal
    """
    return patient_portal(request)

