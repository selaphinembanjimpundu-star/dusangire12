#!/usr/bin/env python
"""Script to run makemigrations for Phase 2.2"""
import os
import sys
import django
from io import StringIO

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dusangire.settings')
django.setup()

from django.core.management import call_command

# Redirect input to provide default answer
old_stdin = sys.stdin
sys.stdin = StringIO('1\n')

try:
    call_command('makemigrations', 'subscriptions')
finally:
    sys.stdin = old_stdin
