from django.db import migrations
from django.utils.timezone import now


def create_currency(apps, schema_editor):
    Currency = apps.get_model('trackshop', 'Currency')

    Currency.objects.get_or_create(
        code='USD',
        defaults={'name': 'Dollar US', 'symbol': '$'}
    )

    Currency.objects.get_or_create(
        code='CDF',
        defaults={'name': 'Franc Congolais', 'symbol': 'FC'}
    )

    ExchangeRate = apps.get_model('trackshop', 'ExchangeRate')
    usd_currency = Currency.objects.get(code='USD')
    cdf_currency = Currency.objects.get(code='CDF') 

    ExchangeRate.objects.get_or_create(
        from_currency=usd_currency,
        to_currency=usd_currency,
        defaults={'rate': 1.0, 'date': now().date()}
    )

    ExchangeRate.objects.get_or_create(
        from_currency=cdf_currency,
        to_currency=cdf_currency,
        defaults={'rate': 1.0, 'date': now().date()}
    )
    ExchangeRate.objects.get_or_create(
        from_currency=usd_currency,
        to_currency=cdf_currency,
        defaults={'rate': 2000.0, 'date': now().date()}  # Example rate, adjust as needed
    )

    ExchangeRate.objects.get_or_create(
        from_currency=cdf_currency,
        to_currency=usd_currency,
        defaults={'rate': 0.0004, 'date': now().date()}  # Example rate, adjust as needed
    )

class Migration(migrations.Migration):
    dependencies = [
            ('trackshop', '0001_initial'), 
        ]

    operations = [
            migrations.RunPython(create_currency)
        ]

    