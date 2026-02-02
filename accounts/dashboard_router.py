"""
Role-Based Dashboard Router
Handles routing users to appropriate dashboards based on their roles
"""

from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import UserRole
import logging

logger = logging.getLogger(__name__)


ROLE_DASHBOARD_MAPPING = {
    UserRole.PATIENT: 'customer_dashboard:dashboard',
    UserRole.CAREGIVER: 'customer_dashboard:dashboard',
    UserRole.NUTRITIONIST: 'nutritionist_dashboard:dashboard',
    UserRole.MEDICAL_STAFF: 'hospital_wards:medical_staff_dashboard',
    UserRole.CHEF: 'catering:chef_dashboard',
    UserRole.KITCHEN_STAFF: 'catering:kitchen_staff_dashboard',
    UserRole.DELIVERY_PERSON: 'delivery:delivery_dashboard',
    UserRole.SUPPORT_STAFF: 'support:staff_dashboard',
    UserRole.HOSPITAL_MANAGER: 'hospital_wards:hospital_manager_dashboard',
    UserRole.ADMIN: 'admin_dashboard:dashboard',
}


@login_required
def dashboard_redirect(request):
    """
    Route authenticated users to their role-specific dashboard
    """
    user = request.user
    
    # Get user role from profile
    try:
        role = user.profile.role
    except Exception as e:
        logger.error(f"Error getting user profile for user {user.id}: {e}")
        messages.error(request, "Unable to determine your account type. Please contact support.")
        return redirect('home')
    
    # Check user account status
    if hasattr(user, 'profile') and not user.profile.is_active:
        messages.warning(request, "Your account has been disabled. Please contact support.")
        return redirect('home')
    
    # Map role to dashboard
    dashboard_url = ROLE_DASHBOARD_MAPPING.get(role)
    
    if not dashboard_url:
        logger.warning(f"No dashboard mapping for role: {role}")
        messages.error(request, "Dashboard for your role is not yet configured.")
        return redirect('home')
    
    logger.info(f"Redirecting user {user.username} (role: {role}) to {dashboard_url}")
    return redirect(dashboard_url)


@login_required
def dashboard_home(request):
    """
    Unified dashboard home page that displays available dashboards for user's role
    """
    user = request.user
    role = user.profile.role if hasattr(user, 'profile') else None
    
    # Get dashboard info
    dashboard_info = get_dashboard_info(role)
    
    context = {
        'user': user,
        'role': role,
        'dashboard_info': dashboard_info,
        'title': 'Dashboard',
    }
    
    return render(request, 'accounts/dashboard_home.html', context)


def get_dashboard_info(role):
    """
    Get information about available dashboards for a role
    """
    dashboard_descriptions = {
        UserRole.PATIENT: {
            'name': 'Customer Dashboard',
            'description': 'View your orders, meal plans, health profiles, and loyalty points',
            'icon': 'bi-person',
            'color': 'primary',
        },
        UserRole.CAREGIVER: {
            'name': 'Caregiver Dashboard',
            'description': 'Manage patient care, view health information, and coordinate nutrition',
            'icon': 'bi-heart',
            'color': 'danger',
        },
        UserRole.NUTRITIONIST: {
            'name': 'Nutritionist Dashboard',
            'description': 'Create meal plans, track client nutrition, and manage dietary preferences',
            'icon': 'bi-apple',
            'color': 'success',
        },
        UserRole.MEDICAL_STAFF: {
            'name': 'Medical Staff Dashboard',
            'description': 'Manage patient admissions, wards, beds, and medical care',
            'icon': 'bi-hospital',
            'color': 'info',
        },
        UserRole.CHEF: {
            'name': 'Chef Dashboard',
            'description': 'View meal orders, manage kitchen operations, and track inventory',
            'icon': 'bi-cup-hot',
            'color': 'warning',
        },
        UserRole.KITCHEN_STAFF: {
            'name': 'Kitchen Staff Dashboard',
            'description': 'Track meal preparation tasks and delivery schedules',
            'icon': 'bi-cup-hot',
            'color': 'warning',
        },
        UserRole.DELIVERY_PERSON: {
            'name': 'Delivery Dashboard',
            'description': 'View delivery routes, manage deliveries, and track real-time locations',
            'icon': 'bi-truck',
            'color': 'secondary',
        },
        UserRole.SUPPORT_STAFF: {
            'name': 'Support Staff Dashboard',
            'description': 'Handle customer support tickets and inquiries',
            'icon': 'bi-chat-dots',
            'color': 'light',
        },
        UserRole.HOSPITAL_MANAGER: {
            'name': 'Hospital Manager Dashboard',
            'description': 'Manage hospital operations, wards, staff, and nutrition programs',
            'icon': 'bi-building',
            'color': 'dark',
        },
        UserRole.ADMIN: {
            'name': 'Admin Dashboard',
            'description': 'System administration, analytics, user management, and configuration',
            'icon': 'bi-gear',
            'color': 'danger',
        },
    }
    
    return dashboard_descriptions.get(role, {})


def get_role_permissions(role):
    """
    Define role-based permissions and features
    """
    permissions_map = {
        UserRole.PATIENT: {
            'features': [
                'view_orders',
                'view_meals',
                'manage_delivery_addresses',
                'view_health_profile',
                'earn_loyalty_points',
                'view_subscriptions',
                'access_nutritionist_consultation',
            ],
            'can_manage_users': False,
            'can_view_analytics': False,
        },
        UserRole.CAREGIVER: {
            'features': [
                'view_patient_orders',
                'manage_patient_health',
                'coordinate_nutrition',
                'track_wellness',
            ],
            'can_manage_users': False,
            'can_view_analytics': False,
        },
        UserRole.NUTRITIONIST: {
            'features': [
                'create_meal_plans',
                'manage_clients',
                'track_nutrition',
                'create_education_content',
                'view_analytics',
            ],
            'can_manage_users': False,
            'can_view_analytics': True,
        },
        UserRole.MEDICAL_STAFF: {
            'features': [
                'manage_patient_admission',
                'manage_wards',
                'manage_beds',
                'schedule_deliveries',
                'view_patient_health',
                'manage_education',
            ],
            'can_manage_users': False,
            'can_view_analytics': True,
        },
        UserRole.CHEF: {
            'features': [
                'view_meal_orders',
                'manage_kitchen_operations',
                'track_inventory',
                'manage_team',
            ],
            'can_manage_users': False,
            'can_view_analytics': True,
        },
        UserRole.KITCHEN_STAFF: {
            'features': [
                'view_meal_orders',
                'update_meal_status',
                'track_tasks',
            ],
            'can_manage_users': False,
            'can_view_analytics': False,
        },
        UserRole.DELIVERY_PERSON: {
            'features': [
                'view_delivery_routes',
                'manage_deliveries',
                'track_location',
                'update_delivery_status',
            ],
            'can_manage_users': False,
            'can_view_analytics': False,
        },
        UserRole.SUPPORT_STAFF: {
            'features': [
                'view_support_tickets',
                'manage_tickets',
                'view_faq',
            ],
            'can_manage_users': False,
            'can_view_analytics': False,
        },
        UserRole.HOSPITAL_MANAGER: {
            'features': [
                'manage_hospital_operations',
                'manage_wards',
                'manage_staff',
                'manage_nutrition_program',
                'view_analytics',
                'manage_budgets',
            ],
            'can_manage_users': True,
            'can_view_analytics': True,
        },
        UserRole.ADMIN: {
            'features': [
                'manage_all_users',
                'manage_system',
                'view_analytics',
                'manage_configuration',
                'manage_permissions',
            ],
            'can_manage_users': True,
            'can_view_analytics': True,
        },
    }
    
    return permissions_map.get(role, {'features': [], 'can_manage_users': False, 'can_view_analytics': False})
