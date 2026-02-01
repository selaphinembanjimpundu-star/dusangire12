import os
import django
import sys

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dusangire.settings')
django.setup()

from django.contrib.auth.models import User
from corporate.models import CorporatePartner, CorporateContract, CorporateEmployee
from nutritionist_dashboard.models import NutritionistProfile, NutritionistAvailability, Consultation
from catering.models import CateringPackage, CateringBooking
from subscriptions.models import SubscriptionPlan, PlanCategory
from decimal import Decimal
from django.utils import timezone
from datetime import time, timedelta

def verify_phase4():
    print("--- VERIFYING PHASE 4: REVENUE STREAMS & DASHBOARDS ---")
    
    # 1. Verify Corporate Contracts
    print("\n1. Verifying Corporate Contracts...")
    partner, _ = CorporatePartner.objects.get_or_create(
        name="Test Corp",
        email="contact@testcorp.com"
    )
    contract, _ = CorporateContract.objects.get_or_create(
        partner=partner,
        discount_percentage=Decimal('15.00'),
        status='active'
    )
    user, _ = User.objects.get_or_create(username="corp_employee")
    employee, _ = CorporateEmployee.objects.get_or_create(
        user=user,
        partner=partner,
        is_active=True
    )
    print(f"✅ Corporate Partner: {partner.name}")
    print(f"✅ Corporate Contract: {contract.discount_percentage}% discount")
    print(f"✅ Corporate Employee: {employee.user.username}")

    # 2. Verify Nutritionist Consultations
    print("\n2. Verifying Nutritionist Consultations...")
    nutri_user, _ = User.objects.get_or_create(username="nutritionist_1")
    profile, _ = NutritionistProfile.objects.get_or_create(
        user=nutri_user,
        defaults={'specialization': 'Clinical Nutrition', 'status': 'active'}
    )
    availability, _ = NutritionistAvailability.objects.get_or_create(
        nutritionist=nutri_user,
        day_of_week=1, # Tuesday
        start_time=time(9, 0),
        end_time=time(17, 0)
    )
    print(f"✅ Nutritionist Profile: {profile.specialization}")
    print(f"✅ Nutritionist Availability: {availability.get_day_of_week_display()} {availability.start_time}-{availability.end_time}")

    # 3. Verify Catering Services
    print("\n3. Verifying Catering Services...")
    package, _ = CateringPackage.objects.get_or_create(
        name="Wedding Feast",
        defaults={'description': 'Full wedding catering', 'price_per_person': Decimal('15000.00'), 'min_people': 50}
    )
    booking, _ = CateringBooking.objects.get_or_create(
        user=user,
        package=package,
        event_name="Test Wedding",
        event_date=timezone.now().date() + timedelta(days=30),
        event_time=time(14, 0),
        location="Kigali Convention Center",
        number_of_people=100
    )
    print(f"✅ Catering Package: {package.name} (RWF {package.price_per_person}/person)")
    print(f"✅ Catering Booking: {booking.event_name}, Total: RWF {booking.total_price}")

    # 4. Verify Specialized Meal Packages
    print("\n4. Verifying Specialized Meal Packages...")
    plan, _ = SubscriptionPlan.objects.get_or_create(
        name="Keto Advanced",
        defaults={
            'description': 'High fat, low carb',
            'category': PlanCategory.KETO,
            'price': Decimal('50000.00'),
            'duration_days': 30,
            'meals_per_cycle': 30
        }
    )
    print(f"✅ Specialized Plan: {plan.name} (Category: {plan.get_category_display()})")

    print("\n--- PHASE 4 VERIFICATION COMPLETE ---")

if __name__ == "__main__":
    verify_phase4()
