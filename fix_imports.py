# fix_imports.py - Place this in your project root (same folder as manage.py)
import os
import sys

print("=" * 60)
print("Fixing Import Issues")
print("=" * 60)

# Add current directory to path
sys.path.insert(0, os.getcwd())

# 1. Fix subscriptions/models.py
print("\n1. Fixing subscriptions/models.py...")
subs_path = os.path.join('subscriptions', 'models.py')
try:
    with open(subs_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove the circular import line
    lines = content.split('\n')
    fixed_lines = []
    removed = False
    
    for i, line in enumerate(lines):
        if ('from subscriptions.models import Subscription' in line or 
            '#from subscriptions.models import Subscription' in line):
            print(f"  Removing circular import on line {i+1}: {line.strip()}")
            removed = True
            continue
        fixed_lines.append(line)
    
    if removed:
        with open(subs_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(fixed_lines))
        print("  ✓ Fixed circular import")
    else:
        print("  ✓ No circular import found")
        
except FileNotFoundError:
    print(f"  ✗ File not found: {subs_path}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# 2. Fix payments/models.py
print("\n2. Fixing payments/models.py...")
payments_path = os.path.join('payments', 'models.py')
try:
    with open(payments_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check and fix the import
    if 'from subscriptions.models import UserSubscription' in content:
        content = content.replace(
            'from subscriptions.models import UserSubscription',
            'from subscriptions.models import Subscription'
        )
        with open(payments_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  ✓ Changed UserSubscription to Subscription import")
    else:
        print("  ✓ Import already correct")
        
except FileNotFoundError:
    print(f"  ✗ File not found: {payments_path}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# 3. Fix customer_dashboard/views.py
print("\n3. Fixing customer_dashboard/views.py...")
customer_path = os.path.join('customer_dashboard', 'views.py')
try:
    with open(customer_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if there's a problematic Subscription import
    lines = content.split('\n')
    fixed_lines = []
    changed = False
    
    for i, line in enumerate(lines):
        if 'from subscriptions.models import' in line:
            # Make sure it imports Subscription correctly
            if 'UserSubscription' in line:
                new_line = line.replace('UserSubscription', 'Subscription')
                print(f"  Changing line {i+1}: {line.strip()} -> {new_line.strip()}")
                fixed_lines.append(new_line)
                changed = True
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    if changed:
        with open(customer_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(fixed_lines))
        print("  ✓ Fixed Subscription import")
    else:
        print("  ✓ Import already correct")
        
except FileNotFoundError:
    print(f"  ✗ File not found: {customer_path}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# 4. Create a test to verify imports work
print("\n4. Testing imports...")
test_code = '''
try:
    from subscriptions.models import Subscription
    print("  ✓ Successfully imported Subscription")
except ImportError as e:
    print(f"  ✗ Failed to import Subscription: {e}")

try:
    from subscriptions.models import SubscriptionPlan
    print("  ✓ Successfully imported SubscriptionPlan")
except ImportError as e:
    print(f"  ✗ Failed to import SubscriptionPlan: {e}")
'''

try:
    # Create test file
    test_file = 'test_imports.py'
    with open(test_file, 'w') as f:
        f.write(test_code)
    
    # Run test
    import subprocess
    result = subprocess.run([sys.executable, test_file], capture_output=True, text=True)
    print(result.stdout)
    
    # Clean up
    if os.path.exists(test_file):
        os.remove(test_file)
        
except Exception as e:
    print(f"  ✗ Test failed: {e}")

print("\n" + "=" * 60)
print("FIX COMPLETE!")
print("=" * 60)
print("\nNext steps:")
print("1. Run: python manage.py makemigrations")
print("2. Run: python manage.py migrate")
print("3. Run: python manage.py runserver")
print("\nIf you still have issues, check:")
print("  - No circular imports in subscriptions/models.py")
print("  - All files import 'Subscription' not 'UserSubscription'")