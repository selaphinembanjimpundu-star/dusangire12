import os
import django
import sys

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dusangire.settings')
django.setup()

from django.db import connection

def check_column():
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info(orders_order)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        if 'corporate_discount_amount' in column_names:
            print("SUCCESS: corporate_discount_amount column exists!")
        else:
            print("FAILURE: corporate_discount_amount column NOT found.")
            print(f"Existing columns: {column_names}")

if __name__ == "__main__":
    check_column()
