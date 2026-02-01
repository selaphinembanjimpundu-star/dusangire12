"""
Professional account validation utilities for payment processing
Validates user accounts, phone numbers, emails, and payment details
"""

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


class AccountValidationError(Exception):
    """Custom exception for account validation errors"""
    pass


def validate_uganda_phone_number(phone_number):
    """
    Validate Uganda phone number format
    Accepts formats: 0781234567, +256781234567, 256781234567
    """
    if not phone_number:
        return False
    
    # Remove spaces, dashes, and other characters
    cleaned = re.sub(r'[\s\-\(\)]', '', phone_number)
    
    # Remove leading + if present
    if cleaned.startswith('+'):
        cleaned = cleaned[1:]
    
    # Check if it's a valid Uganda mobile number
    # Uganda mobile numbers: 256 + 7XX + 6 digits (total 12 digits)
    # Or local format: 07XX + 6 digits (total 9 digits)
    
    # Local format (9 digits starting with 0)
    if re.match(r'^0[7][0-9]{8}$', cleaned):
        return True
    
    # International format (12 digits starting with 256)
    if re.match(r'^256[7][0-9]{8}$', cleaned):
        return True
    
    return False


def format_uganda_phone_number(phone_number):
    """
    Format Uganda phone number to standard format (256XXXXXXXXX)
    """
    if not phone_number:
        return None
    
    # Remove spaces, dashes, and other characters
    cleaned = re.sub(r'[\s\-\(\)]', '', phone_number)
    
    # Remove leading + if present
    if cleaned.startswith('+'):
        cleaned = cleaned[1:]
    
    # Convert local format (07XXXXXXXX) to international (2567XXXXXXXX)
    if cleaned.startswith('0') and len(cleaned) == 10:
        cleaned = '256' + cleaned[1:]
    
    # Ensure it starts with 256
    if not cleaned.startswith('256'):
        return None
    
    return cleaned


def validate_email_format(email):
    """Validate email format"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_account_for_payment(user):
    """
    Validate user account is ready for payment processing
    
    Returns:
        dict: {
            'valid': bool,
            'errors': list,
            'warnings': list
        }
    """
    errors = []
    warnings = []
    
    # Check if user is active
    if not user.is_active:
        errors.append("Your account is inactive. Please contact support.")
    
    # Check if email is set and valid
    if not user.email:
        errors.append("Email address is required for payment processing.")
    elif not validate_email_format(user.email):
        errors.append("Invalid email address format.")
    
    # Check if profile exists
    if not hasattr(user, 'profile'):
        errors.append("User profile is missing. Please complete your profile.")
    else:
        profile = user.profile
        
        # Check if phone number is set and valid
        if not profile.phone:
            warnings.append("Phone number is recommended for payment processing.")
        elif not validate_uganda_phone_number(profile.phone):
            warnings.append("Phone number format may be invalid. Please verify.")
    
    # Check if user has completed basic information
    if not user.first_name or not user.last_name:
        warnings.append("Complete your name for better payment processing.")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }


def validate_payment_method_details(payment_method, phone_number=None, account_number=None):
    """
    Validate payment method specific details
    
    Args:
        payment_method: Payment method code
        phone_number: Phone number for mobile money
        account_number: Account number for bank transfer
    
    Returns:
        dict: {
            'valid': bool,
            'errors': list
        }
    """
    errors = []
    
    # Mobile money validation
    if payment_method in ['mtn_mobile_money', 'airtel_money']:
        if not phone_number:
            errors.append("Phone number is required for mobile money payments.")
        elif not validate_uganda_phone_number(phone_number):
            errors.append("Invalid phone number format. Please use format: 0781234567 or +256781234567")
    
    # Bank transfer validation
    elif payment_method == 'bank_transfer':
        if not account_number:
            errors.append("Account number is required for bank transfer.")
        elif len(account_number.strip()) < 5:
            errors.append("Account number must be at least 5 characters.")
        elif not re.match(r'^[A-Za-z0-9\s\-]+$', account_number):
            errors.append("Account number contains invalid characters.")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def validate_user_can_make_payment(user, payment_method, phone_number=None, account_number=None):
    """
    Comprehensive validation before allowing payment
    
    Returns:
        dict: {
            'valid': bool,
            'errors': list,
            'warnings': list
        }
    """
    # Validate account
    account_validation = validate_account_for_payment(user)
    
    # Validate payment method details
    payment_validation = validate_payment_method_details(
        payment_method, 
        phone_number, 
        account_number
    )
    
    # Combine results
    all_errors = account_validation['errors'] + payment_validation['errors']
    all_warnings = account_validation['warnings']
    
    return {
        'valid': account_validation['valid'] and payment_validation['valid'],
        'errors': all_errors,
        'warnings': all_warnings
    }













