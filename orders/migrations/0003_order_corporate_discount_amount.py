from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_order_coupon_code_order_discount_amount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='corporate_discount_amount',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10),
        ),
    ]
