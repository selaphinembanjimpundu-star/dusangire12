from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import UserRole
import logging

logger = logging.getLogger(__name__)


def register(request):
    """User registration view - Only allows customers without light to register."""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # Additional validation: ensure no_light_confirmation is True
            no_light_confirmation = form.cleaned_data.get('no_light_confirmation')
            if not no_light_confirmation:
                messages.error(
                    request, 
                    'Registration is only available for customers without light. '
                    'Please confirm that you do not have light to proceed.'
                )
                return render(request, 'accounts/register.html', {'form': form})
            
            # Save user - form.save() will automatically set role to CUSTOMER
            user = form.save()
            
            # Double-check security: Ensure role is CUSTOMER (should never be admin/nutritionist)
            if hasattr(user, 'profile') and user.profile.role != UserRole.CUSTOMER:
                user.profile.role = UserRole.CUSTOMER
                user.profile.save()
                messages.warning(
                    request, 
                    'Account created as customer. Admin and staff accounts must be created by administrators.'
                )
            
            username = form.cleaned_data.get('username')
            messages.success(request, f'Customer account created for {username}! You can now log in.')
            login(request, user)
            
            # Redirect to dashboard instead of menu list
            return redirect('accounts:dashboard_redirect')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def signup(request):
    """Signup view - Unified endpoint that serves the same registration flow as `register`.
    This preserves the `/accounts/signup/` URL while using the same logic/template as `register`.
    """
    # Serve the same registration logic for both GET and POST so both URLs behave identically
    return register(request)


def login_view(request):
    """User login view with dashboard redirect"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Get next parameter or default to dashboard redirect
            next_url = request.POST.get('next', '')
            if next_url:
                return redirect(next_url)
            
            # Default to dashboard redirect
            return redirect('accounts:dashboard_redirect')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    # Pass next parameter to template
    next_url = request.GET.get('next', '')
    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


def hospital_ward_login_redirect(request):
    """
    Dedicated redirect view for hospital ward system.
    Routes authenticated users to their role-based hospital dashboard.
    """
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    user = request.user
    logger.info(f"Hospital ward login redirect for user: {user.username}")
    
    # Check if user has a profile
    if not hasattr(user, 'profile'):
        logger.warning(f"No profile found for user {user.id}")
        messages.info(request, 'Please complete your profile setup first.')
        return redirect('accounts:profile')
    
    try:
        profile = user.profile
        
        # Hospital ward roles and their corresponding dashboards
        hospital_ward_routes = {
            'patient': 'hospital_wards:patient_dashboard',
            'caregiver': 'hospital_wards:caregiver_dashboard',
            'nutritionist': 'hospital_wards:nutritionist_dashboard',
            'medical_staff': 'hospital_wards:medical_staff_dashboard',
            'chef': 'hospital_wards:chef_dashboard',
            'kitchen_staff': 'hospital_wards:kitchen_staff_dashboard',
            'delivery_person': 'hospital_wards:delivery_person_dashboard',
            'support_staff': 'hospital_wards:support_staff_dashboard',
            'hospital_manager': 'hospital_wards:hospital_manager_dashboard',
            'admin': 'hospital_wards:admin_dashboard',
        }
        
        # Route to appropriate hospital dashboard
        if profile.role in hospital_ward_routes:
            target_dashboard = hospital_ward_routes[profile.role]
            logger.info(f"Redirecting {profile.role} user to {target_dashboard}")
            return redirect(target_dashboard)
        else:
            logger.warning(f"User {user.id} has role '{profile.role}' which is not a hospital ward role")
            messages.error(request, 'Your account role is not configured for the hospital system. Please contact administrator.')
            return redirect('home')
            
    except Exception as e:
        logger.error(f"Critical error in hospital_ward_login_redirect for user {user.id}: {str(e)}")
        messages.error(request, 'An error occurred while redirecting to your hospital dashboard.')
        return redirect('home')

@login_required
def dashboard_redirect(request):
    """
    Redirect user to appropriate dashboard based on role.
    Supports both main system roles and hospital ward roles.
    """
    user = request.user
    logger.info(f"Dashboard redirect for user: {user.username}")
    
    # Check if user has a profile
    if not hasattr(user, 'profile'):
        logger.warning(f"No profile found for user {user.id}")
        messages.info(request, 'Please complete your profile setup first.')
        return redirect('accounts:profile')
    
    try:
        profile = user.profile
        
        # ==================== HOSPITAL WARD ROLES ====================
        # Map hospital ward roles to their dashboard templates
        hospital_ward_roles = {
            'patient': 'hospital_wards:patient_dashboard',
            'caregiver': 'hospital_wards:caregiver_dashboard',
            'nutritionist': 'hospital_wards:nutritionist_dashboard',
            'medical_staff': 'hospital_wards:medical_staff_dashboard',
            'chef': 'hospital_wards:chef_dashboard',
            'kitchen_staff': 'hospital_wards:kitchen_staff_dashboard',
            'delivery_person': 'hospital_wards:delivery_person_dashboard',
            'support_staff': 'hospital_wards:support_staff_dashboard',
            'hospital_manager': 'hospital_wards:hospital_manager_dashboard',
            'admin': 'hospital_wards:admin_dashboard',
        }
        
        # Check if user's role matches hospital ward roles
        if profile.role in hospital_ward_roles:
            target_view = hospital_ward_roles[profile.role]
            logger.info(f"Redirecting {profile.role} to {target_view}")
            return redirect(target_view)
        
        # ==================== MAIN SYSTEM ROLES ====================
        # ADMIN - Redirect to main admin dashboard
        if profile.role == UserRole.ADMIN:
            logger.info("Redirecting ADMIN to admin dashboard")
            return redirect('/dashboard/')
        
        # NUTRITIONIST - Old system (legacy support)
        elif profile.role == UserRole.NUTRITIONIST:
            logger.info("Redirecting NUTRITIONIST to nutritionist dashboard")
            try:
                from nutritionist_dashboard.models import NutritionistProfile
                nutritionist_profile = NutritionistProfile.objects.get(user=user)
                return redirect('/nutritionist/')
            except NutritionistProfile.DoesNotExist:
                logger.info("Nutritionist profile not found, redirecting to create profile")
                return redirect('/nutritionist/create-profile/')
            except ImportError as e:
                logger.error(f"Nutritionist dashboard not available: {e}")
                messages.error(request, 'Nutritionist dashboard is not available. Please contact administrator.')
                return redirect('home')
        
        # KITCHEN STAFF - Old system (legacy support)
        elif profile.role == UserRole.KITCHEN_STAFF:
            logger.info("Redirecting KITCHEN_STAFF to kitchen dashboard")
            return redirect('/dashboard/kitchen/')
        
        # DELIVERY PERSON - Old system (legacy support)
        elif profile.role == UserRole.DELIVERY_PERSON:
            logger.info("Redirecting DELIVERY_PERSON to delivery dashboard")
            return redirect('/dashboard/orders/')
        
        # CUSTOMER - Default role
        elif profile.role == UserRole.CUSTOMER:
            logger.info("Redirecting CUSTOMER to customer dashboard")
            return redirect('/customer_dashboard/')
        
        # Unknown role
        else:
            logger.warning(f"Unknown role for user {user.id}: {profile.role}")
            messages.warning(request, 'Your account role is not configured properly.')
            return redirect('home')
            
    except Exception as e:
        logger.error(f"Critical error in dashboard_redirect for user {user.id}: {str(e)}")
        messages.error(request, 'An error occurred while redirecting to your dashboard.')
        return redirect('home')


@login_required
def profile(request):
    """User profile view"""
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('accounts:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'accounts/profile.html', context)


def get_user_dashboard_url(user):
    """
    Helper function to get dashboard URL for a user.
    Returns direct URLs to avoid namespace issues.
    """
    if hasattr(user, 'profile'):
        if user.profile.role == UserRole.ADMIN:
            return '/dashboard/'
        elif user.profile.role == UserRole.NUTRITIONIST:
            return '/nutritionist/'
        elif user.profile.role == UserRole.KITCHEN_STAFF:
            return '/dashboard/kitchen/'
        elif user.profile.role == UserRole.DELIVERY_PERSON:
            return '/dashboard/orders/'
        elif user.profile.role == UserRole.CUSTOMER:
            return '/customer_dashboard/'
    
    return '/'  # Home page


def check_user_access(request, required_role):
    """Check if user has required role for access"""
    if not request.user.is_authenticated:
        return False
    
    if hasattr(request.user, 'profile'):
        return request.user.profile.role == required_role
    
    return False


@login_required
def switch_dashboard(request):
    """Allow users with multiple roles to switch between dashboards (if applicable)"""
    # For now, just redirect to their primary role dashboard
    return redirect('accounts:dashboard_redirect')