"""
Role-Based View Mixins for DUSANGIRE
Provides class-based view mixins for role-based access control
"""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages
from accounts.models import UserRole
from accounts.rbac import ROLE_PERMISSIONS, get_user_dashboard_url


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin to check if user has one of the allowed roles.
    Usage in view: allowed_roles = [UserRole.PATIENT, UserRole.CAREGIVER]
    """
    allowed_roles = []
    
    def test_func(self):
        if not hasattr(self.request.user, 'profile'):
            return False
        return self.request.user.profile.role in self.allowed_roles
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('accounts:login')
        
        messages.error(
            self.request,
            f'Access denied. This page is only accessible to: {", ".join([ROLE_PERMISSIONS.get(r, {}).get("name", r) for r in self.allowed_roles])}'
        )
        return HttpResponseForbidden("You do not have permission to access this page.")


class PermissionRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin to check if user has specific permissions.
    Usage in view: required_permissions = ['create_meal_plans', 'manage_patients']
    """
    required_permissions = []
    
    def test_func(self):
        if not hasattr(self.request.user, 'profile'):
            return False
        
        user_role = self.request.user.profile.role
        user_permissions = ROLE_PERMISSIONS.get(user_role, {}).get('permissions', [])
        
        return all(perm in user_permissions for perm in self.required_permissions)
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('accounts:login')
        
        missing_perms = []
        if hasattr(self.request.user, 'profile'):
            user_role = self.request.user.profile.role
            user_permissions = ROLE_PERMISSIONS.get(user_role, {}).get('permissions', [])
            missing_perms = [p for p in self.required_permissions if p not in user_permissions]
        
        messages.error(
            self.request,
            f'Access denied. You do not have the required permission(s): {", ".join(missing_perms)}'
        )
        return HttpResponseForbidden("You do not have the required permissions.")


class ActiveUserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin to check if user account is active.
    """
    def test_func(self):
        if not hasattr(self.request.user, 'profile'):
            return False
        
        profile = self.request.user.profile
        return profile.is_active and profile.status == 'active'
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('accounts:login')
        
        messages.error(self.request, 'Your account is not active. Please contact support.')
        return HttpResponseForbidden("Your account is not active.")


class PatientOnlyMixin(RoleRequiredMixin):
    """Restrict view to patients only"""
    allowed_roles = [UserRole.PATIENT]


class CaregiverOnlyMixin(RoleRequiredMixin):
    """Restrict view to caregivers only"""
    allowed_roles = [UserRole.CAREGIVER]


class PatientOrCaregiverMixin(RoleRequiredMixin):
    """Restrict view to patients and caregivers"""
    allowed_roles = [UserRole.PATIENT, UserRole.CAREGIVER]


class HealthcareProviderMixin(RoleRequiredMixin):
    """Restrict view to nutritionists and medical staff"""
    allowed_roles = [UserRole.NUTRITIONIST, UserRole.MEDICAL_STAFF]


class NutritionistOnlyMixin(RoleRequiredMixin):
    """Restrict view to nutritionists only"""
    allowed_roles = [UserRole.NUTRITIONIST]


class MedicalStaffOnlyMixin(RoleRequiredMixin):
    """Restrict view to medical staff only"""
    allowed_roles = [UserRole.MEDICAL_STAFF]


class StaffMemberMixin(RoleRequiredMixin):
    """Restrict view to staff members"""
    allowed_roles = [
        UserRole.CHEF,
        UserRole.KITCHEN_STAFF,
        UserRole.DELIVERY_PERSON,
        UserRole.SUPPORT_STAFF,
        UserRole.HOSPITAL_MANAGER,
    ]


class KitchenStaffMixin(RoleRequiredMixin):
    """Restrict view to kitchen staff (chef or kitchen staff)"""
    allowed_roles = [UserRole.CHEF, UserRole.KITCHEN_STAFF]


class DeliveryPersonMixin(RoleRequiredMixin):
    """Restrict view to delivery personnel"""
    allowed_roles = [UserRole.DELIVERY_PERSON]


class SupportStaffMixin(RoleRequiredMixin):
    """Restrict view to support staff"""
    allowed_roles = [UserRole.SUPPORT_STAFF]


class HospitalManagerMixin(RoleRequiredMixin):
    """Restrict view to hospital managers"""
    allowed_roles = [UserRole.HOSPITAL_MANAGER]


class AdminOnlyMixin(RoleRequiredMixin):
    """Restrict view to system administrators"""
    allowed_roles = [UserRole.ADMIN]


class ManagementMixin(RoleRequiredMixin):
    """Restrict view to management (hospital manager or admin)"""
    allowed_roles = [UserRole.HOSPITAL_MANAGER, UserRole.ADMIN]
