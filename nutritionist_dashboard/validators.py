"""
Custom validators for nutritionist dashboard models and forms.
"""

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_phone_number(value):
    """
    Validate phone number format.
    Accepts international format with +, dashes, spaces, and parentheses.
    Minimum 7 digits required.
    """
    if not value:
        return

    # Remove common formatting characters
    cleaned = re.sub(r'[\s\-\(\)\+]', '', value)

    # Must contain at least 7 digits
    if not re.search(r'\d{7,}', cleaned):
        raise ValidationError(
            _('Please enter a valid phone number with at least 7 digits.'),
            code='invalid_phone'
        )

    # Must not have more than 15 digits (E.164 standard)
    if len(cleaned) > 15:
        raise ValidationError(
            _('Phone number appears to be too long.'),
            code='phone_too_long'
        )


def validate_license_number(value):
    """
    Validate professional license number format.
    Can contain letters, numbers, hyphens, and underscores.
    Minimum 3 characters, maximum 50 characters.
    """
    if not value:
        return

    # Check length
    if len(value) < 3:
        raise ValidationError(
            _('License number must be at least 3 characters long.'),
            code='license_too_short'
        )

    if len(value) > 50:
        raise ValidationError(
            _('License number must be less than 50 characters.'),
            code='license_too_long'
        )

    # Check format (alphanumeric, hyphens, underscores only)
    if not re.match(r'^[a-zA-Z0-9\-_]+$', value):
        raise ValidationError(
            _('License number can only contain letters, numbers, hyphens, and underscores.'),
            code='invalid_license_format'
        )


def validate_specialization(value):
    """
    Validate specialization field.
    Maximum 255 characters, no special characters except spaces, hyphens.
    """
    if not value:
        return

    if len(value) > 255:
        raise ValidationError(
            _('Specialization must be less than 255 characters.'),
            code='specialization_too_long'
        )

    # Check for reasonable characters
    if not re.match(r'^[a-zA-Z0-9\s\-&(),\.\']+$', value):
        raise ValidationError(
            _('Specialization contains invalid characters.'),
            code='invalid_specialization'
        )


def validate_max_clients(value):
    """
    Validate maximum number of clients a nutritionist can manage.
    Must be between 1 and 500.
    """
    if value < 1:
        raise ValidationError(
            _('You must be able to manage at least 1 client.'),
            code='min_clients_error'
        )

    if value > 500:
        raise ValidationError(
            _('Maximum clients cannot exceed 500.'),
            code='max_clients_exceeded'
        )


def validate_bio_length(value):
    """
    Validate biography length.
    Maximum 1000 characters.
    """
    if not value:
        return

    if len(value) > 1000:
        raise ValidationError(
            _('Biography must be less than 1000 characters.'),
            code='bio_too_long'
        )

    # Check minimum length when provided
    if len(value) < 10:
        raise ValidationError(
            _('Biography must be at least 10 characters long.'),
            code='bio_too_short'
        )


def validate_assignment_dates(start_date, end_date):
    """
    Validate that end_date is after start_date if both provided.
    """
    if not (start_date and end_date):
        return

    if end_date < start_date:
        raise ValidationError(
            _('End date must be after start date.'),
            code='invalid_date_range'
        )

    # Check for reasonable date ranges (not more than 5 years)
    from datetime import timedelta
    max_duration = timedelta(days=365 * 5)
    if (end_date - start_date) > max_duration:
        raise ValidationError(
            _('Assignment duration cannot exceed 5 years.'),
            code='duration_too_long'
        )
