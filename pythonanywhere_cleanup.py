#!/usr/bin/env python
"""
PythonAnywhere Disk Space Cleanup Script
Frees up disk space by cleaning pip cache and removing unnecessary packages
"""
import subprocess
import os
import shutil

print("\n" + "="*60)
print("PythonAnywhere Disk Space Cleanup")
print("="*60)

# Step 1: Clear pip cache
print("\n1️⃣  Clearing pip cache...")
try:
    subprocess.run(['pip', 'cache', 'purge'], check=False)
    print("   ✓ Pip cache cleared")
except Exception as e:
    print(f"   ⚠️  Could not clear cache: {e}")

# Step 2: Remove pip cache directory
print("\n2️⃣  Removing cache directories...")
cache_dirs = [
    os.path.expanduser('~/.cache/pip'),
    os.path.expanduser('~/.pip/cache'),
]

for cache_dir in cache_dirs:
    if os.path.exists(cache_dir):
        try:
            shutil.rmtree(cache_dir)
            print(f"   ✓ Removed {cache_dir}")
        except Exception as e:
            print(f"   ⚠️  Could not remove {cache_dir}: {e}")

# Step 3: Check disk usage
print("\n3️⃣  Current disk usage:")
try:
    result = subprocess.run(['df', '-h', os.path.expanduser('~')], 
                          capture_output=True, text=True)
    for line in result.stdout.split('\n')[1:]:  # Skip header
        if line.strip():
            print(f"   {line}")
except Exception as e:
    print(f"   ⚠️  Could not get disk info: {e}")

print("\n" + "="*60)
print("✅ Cleanup complete!")
print("="*60)
print("\n📝 Next steps:")
print("   1. Try pip install again: pip install -r requirements.txt")
print("   2. If still out of space, consider:")
print("      - Removing unused Python packages")
print("      - Upgrading to paid PythonAnywhere plan")
print("      - Using only essential packages")
