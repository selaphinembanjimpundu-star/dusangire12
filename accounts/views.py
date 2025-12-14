from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import UserRole


def register(request):
    """User registration view - Only allows customers without light to register.
    
    Security: This endpoint ONLY creates CUSTOMER accounts.
    Admin and nutritionist accounts must be created through Django admin or management commands.
    """
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
            return redirect('menu:menu_list')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


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
