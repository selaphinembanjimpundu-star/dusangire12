#!/usr/bin/env python
"""
Quick template validation script
"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dusangire.settings')

import django
django.setup()

from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist

# List of all known templates from views
TEMPLATES_TO_CHECK = [
    'base.html',
    'home.html',
    'navbar.html',
    'footer.html',
    'accounts/login.html',
    'accounts/register.html',
    'accounts/profile.html',
    'accounts/password_reset.html',
    'accounts/password_reset_done.html',
    'accounts/password_reset_confirm.html',
    'accounts/password_reset_complete.html',
    'accounts/logout.html',
    'support/create_ticket.html',
    'support/ticket_list.html',
    'support/ticket_detail.html',
    'support/staff_ticket_list.html',
    'support/staff_ticket_detail.html',
    'support/feedback.html',
    'support/faq.html',
    'support/staff_dashboard.html',
    'subscriptions/plans.html',
    'subscriptions/subscribe.html',
    'subscriptions/my_subscriptions.html',
    'subscriptions/subscription_detail.html',
    'subscriptions/pause_subscription.html',
    'subscriptions/resume_subscription.html',
    'subscriptions/cancel_subscription.html',
    'subscriptions/update_subscription.html',
    'reviews/add_review.html',
    'reviews/item_reviews.html',
    'reviews/my_reviews.html',
    'payments/payment_confirmation.html',
    'account/login.html',
    'account/signup.html',
]

print("Checking template availability...\n")

errors = []
success = 0

for template_path in TEMPLATES_TO_CHECK:
    try:
        # Try to load the template
        render_to_string(template_path, {})
        print(f"✓ {template_path}")
        success += 1
    except TemplateDoesNotExist:
        errors.append(f"✗ {template_path} - NOT FOUND")
        print(f"✗ {template_path} - NOT FOUND")
    except Exception as e:
        errors.append(f"✗ {template_path} - ERROR: {str(e)[:60]}")
        print(f"✗ {template_path} - ERROR")

print(f"\n{'='*70}")
print(f"✓ Success: {success}/{len(TEMPLATES_TO_CHECK)}")
if errors:
    print(f"✗ Errors: {len(errors)}")
    print(f"\nERRORS:")
    for error in errors:
        print(f"  {error}")
    sys.exit(1)
else:
    print(f"\n✅ All templates are accessible and working!")
    sys.exit(0)
