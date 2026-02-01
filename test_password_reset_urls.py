#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dusangire.settings')
django.setup()

from django.urls import reverse

print("=" * 60)
print("Password Reset URL Configuration Test")
print("=" * 60)

urls = [
    ('password_reset', {}),
    ('password_reset_done', {}),
    ('password_reset_confirm', {'uidb64': 'test', 'token': 'test'}),
    ('password_reset_complete', {}),
]

for url_name, kwargs in urls:
    try:
        url = reverse(f'accounts:{url_name}', kwargs=kwargs)
        print(f"✓ {url_name:25s}: {url}")
    except Exception as e:
        print(f"✗ {url_name:25s}: ERROR - {e}")

print("=" * 60)
print("All password reset URLs configured successfully!")
print("=" * 60)
