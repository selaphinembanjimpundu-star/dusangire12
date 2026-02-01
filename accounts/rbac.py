"""
Role-Based Access Control (RBAC) for DUSANGIRE
Based on Business Model Canvas roles and responsibilities
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from accounts.models import UserRole


# ==================== ROLE DEFINITIONS ====================
# Define what each role can do based on Business Model Canvas

ROLE_PERMISSIONS = {
    UserRole.PATIENT: {
        'name': 'Patient',
        'description': 'Hospital patient receiving nutrition services',
        'permissions': [
            'view_meal_plans',
            'order_meals',
            'view_health_profile',
            'manage_subscriptions',
            'view_delivery_status',
            'contact_support',
            'view_invoices',
            'book_consultations',
        ],
        'dashboard': '/customer_dashboard/',
    },
    
    UserRole.CAREGIVER: {
        'name': 'Caregiver',
        'description': 'Family member supporting patient care',
        'permissions': [
            'view_patient_health',
            'place_orders_for_patient',
            'coordinate_with_patient',
            'view_delivery_status',
            'contact_support',
            'view_meal_plans',
        ],
        'dashboard': '/caregiver_dashboard/',
    },
    
    UserRole.NUTRITIONIST: {
        'name': 'Nutritionist',
        'description': 'Healthcare professional managing nutrition plans',
        'permissions': [
            'create_meal_plans',
            'manage_patients',
            'create_consultations',
            'view_health_profiles',
            'track_patient_progress',
            'manage_dietary_plans',
            'generate_reports',
            'access_patient_data',
        ],
        'dashboard': '/nutritionist/',
    },
    
    UserRole.MEDICAL_STAFF: {
        'name': 'Medical Staff',
        'description': 'Doctor or nurse coordinating patient care',
        'permissions': [
            'prescribe_meal_plans',
            'view_patient_health',
            'coordinate_nutrition',
            'manage_hospital_patients',
            'view_delivery_status',
            'generate_medical_reports',
            'access_patient_data',
        ],
        'dashboard': '/medical_dashboard/',
    },
    
    UserRole.CHEF: {
        'name': 'Chef',
        'description': 'Head chef overseeing meal preparation',
        'permissions': [
            'manage_menu',
            'view_daily_orders',
            'manage_recipes',
            'manage_kitchen_staff',
            'track_ingredients',
            'quality_control',
            'generate_preparation_reports',
        ],
        'dashboard': '/kitchen_dashboard/',
    },
    
    UserRole.KITCHEN_STAFF: {
        'name': 'Kitchen Staff',
        'description': 'Cook or kitchen team member',
        'permissions': [
            'view_daily_orders',
            'prepare_meals',
            'update_preparation_status',
            'report_issues',
            'view_recipes',
        ],
        'dashboard': '/kitchen_dashboard/',
    },
    
    UserRole.DELIVERY_PERSON: {
        'name': 'Delivery Person',
        'description': 'Delivery staff member',
        'permissions': [
            'view_assigned_deliveries',
            'update_delivery_status',
            'manage_delivery_route',
            'contact_customer',
            'report_delivery_issues',
            'view_customer_info',
        ],
        'dashboard': '/delivery_dashboard/',
    },
    
    UserRole.SUPPORT_STAFF: {
        'name': 'Support Staff',
        'description': '24/7 customer support representative',
        'permissions': [
            'view_orders',
            'handle_support_tickets',
            'process_complaints',
            'contact_customers',
            'manage_refunds',
            'generate_support_reports',
            'view_customer_data',
        ],
        'dashboard': '/support_dashboard/',
    },
    
    UserRole.HOSPITAL_MANAGER: {
        'name': 'Hospital Manager',
        'description': 'Hospital administrator overseeing operations',
        'permissions': [
            'manage_hospital_operations',
            'view_financial_reports',
            'manage_staff',
            'coordinate_departments',
            'manage_partnerships',
            'access_analytics',
            'generate_reports',
            'manage_all_users',
        ],
        'dashboard': '/hospital_manager_dashboard/',
    },
    
    UserRole.ADMIN: {
        'name': 'System Administrator',
        'description': 'System administrator with full access',
        'permissions': [
            'manage_all_users',
            'manage_system_settings',
            'access_admin_panel',
            'view_all_data',
            'generate_system_reports',
            'manage_database',
            'security_management',
        ],
        'dashboard': '/admin/',
    },
}


# ==================== DECORATOR FUNCTIONS ====================

def role_required(*allowed_roles):
    """
    Decorator to check if user has one of the allowed roles.
    Usage: @role_required(UserRole.PATIENT, UserRole.CAREGIVER)
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if hasattr(request.user, 'profile'):
                if request.user.profile.role in allowed_roles:
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(
                        request,
                        f'Access denied. This page is only accessible to: {", ".join([ROLE_PERMISSIONS.get(r, {}).get("name", r) for r in allowed_roles])}'
                    )
                    return HttpResponseForbidden("You do not have permission to access this page.")
            else:
                messages.error(request, 'Please complete your profile setup first.')
                return redirect('accounts:profile')
        return wrapper
    return decorator


def permission_required(*permissions):
    """
    Decorator to check if user has specific permissions.
    Usage: @permission_required('create_meal_plans', 'manage_patients')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if hasattr(request.user, 'profile'):
                user_role = request.user.profile.role
                user_permissions = ROLE_PERMISSIONS.get(user_role, {}).get('permissions', [])
                
                if all(perm in user_permissions for perm in permissions):
                    return view_func(request, *args, **kwargs)
                else:
                    missing_perms = [p for p in permissions if p not in user_permissions]
                    messages.error(
                        request,
                        f'Access denied. You do not have permission(s): {", ".join(missing_perms)}'
                    )
                    return HttpResponseForbidden("You do not have the required permissions.")
            else:
                messages.error(request, 'Please complete your profile setup first.')
                return redirect('accounts:profile')
        return wrapper
    return decorator


def active_user_required(view_func):
    """
    Decorator to check if user account is active.
    Usage: @active_user_required
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'profile'):
            if request.user.profile.is_active and request.user.profile.status == 'active':
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'Your account is not active. Please contact support.')
                return HttpResponseForbidden("Your account is not active.")
        else:
            messages.error(request, 'Please complete your profile setup first.')
            return redirect('accounts:profile')
    return wrapper


# ==================== UTILITY FUNCTIONS ====================

def get_user_dashboard_url(user):
    """Get the dashboard URL for a user based on their role"""
    if hasattr(user, 'profile'):
        role_info = ROLE_PERMISSIONS.get(user.profile.role)
        if role_info:
            return role_info.get('dashboard', '/')
    return '/'


def get_user_role_info(user):
    """Get detailed role information for a user"""
    if hasattr(user, 'profile'):
        return ROLE_PERMISSIONS.get(user.profile.role, {})
    return {}


def check_user_permission(user, permission):
    """Check if user has a specific permission"""
    if hasattr(user, 'profile'):
        user_role = user.profile.role
        user_permissions = ROLE_PERMISSIONS.get(user_role, {}).get('permissions', [])
        return permission in user_permissions
    return False


def check_user_role(user, *allowed_roles):
    """Check if user has one of the allowed roles"""
    if hasattr(user, 'profile'):
        return user.profile.role in allowed_roles
    return False


def get_role_choices():
    """Get formatted role choices for forms"""
    return [
        (role, ROLE_PERMISSIONS.get(role, {}).get('name', role))
        for role in UserRole.choices
    ]


def get_roles_by_category():
    """Get roles organized by category based on Business Model Canvas"""
    return {
        'Customers': [
            (UserRole.PATIENT, ROLE_PERMISSIONS[UserRole.PATIENT]['description']),
            (UserRole.CAREGIVER, ROLE_PERMISSIONS[UserRole.CAREGIVER]['description']),
        ],
        'Healthcare': [
            (UserRole.NUTRITIONIST, ROLE_PERMISSIONS[UserRole.NUTRITIONIST]['description']),
            (UserRole.MEDICAL_STAFF, ROLE_PERMISSIONS[UserRole.MEDICAL_STAFF]['description']),
        ],
        'Operations': [
            (UserRole.CHEF, ROLE_PERMISSIONS[UserRole.CHEF]['description']),
            (UserRole.KITCHEN_STAFF, ROLE_PERMISSIONS[UserRole.KITCHEN_STAFF]['description']),
            (UserRole.DELIVERY_PERSON, ROLE_PERMISSIONS[UserRole.DELIVERY_PERSON]['description']),
            (UserRole.SUPPORT_STAFF, ROLE_PERMISSIONS[UserRole.SUPPORT_STAFF]['description']),
        ],
        'Management': [
            (UserRole.HOSPITAL_MANAGER, ROLE_PERMISSIONS[UserRole.HOSPITAL_MANAGER]['description']),
            (UserRole.ADMIN, ROLE_PERMISSIONS[UserRole.ADMIN]['description']),
        ],
    }


# ==================== CONTEXT PROCESSOR ====================

def rbac_context(request):
    """
    Context processor to add role information to all templates.
    Add to TEMPLATES['OPTIONS']['context_processors'] in settings.py
    """
    context = {
        'user_role': None,
        'user_permissions': [],
        'user_dashboard_url': '/',
        'role_permissions': ROLE_PERMISSIONS,
    }
    
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        context['user_role'] = request.user.profile.role
        context['user_permissions'] = ROLE_PERMISSIONS.get(
            request.user.profile.role, {}
        ).get('permissions', [])
        context['user_dashboard_url'] = get_user_dashboard_url(request.user)
    
    return context
