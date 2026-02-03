#!/bin/bash
# Complete PythonAnywhere deployment fix script
# Run this if migrations fail with foreign key constraint errors

set -e  # Exit on any error

cd ~/dusangire12

echo "=========================================="
echo "PythonAnywhere Deployment Fix"
echo "=========================================="

# Activate virtualenv
echo ""
echo "1. Activating virtual environment..."
source ../../../virtualenvs/dusangire_env/bin/activate

# Fix database issues
echo ""
echo "2. Running database fix script..."
python fix_pythonanywhere_db.py

# Run migrations
echo ""
echo "3. Running migrations..."
python manage.py migrate

# Collect static files
echo ""
echo "4. Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "=========================================="
echo "✓ All done! Reload your web app now."
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Go to PythonAnywhere Dashboard"
echo "2. Click your web app"
echo "3. Click Reload"
echo ""
