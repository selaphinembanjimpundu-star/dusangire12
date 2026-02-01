import os
import django
import sys

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dusangire.settings')
django.setup()

from django.db import connection

def add_column():
    try:
        with connection.cursor() as cursor:
            cursor.execute("ALTER TABLE orders_order ADD COLUMN corporate_discount_amount decimal(10, 2) DEFAULT 0.00 NOT NULL;")
            print("SUCCESS: Column added via SQL.")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    add_column()
