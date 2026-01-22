from django.db import migrations
from django.utils.timezone import now

def create_currency(apps, schema_editor):
    Currency = apps.get_model('trackshop', 'Currency')
    ExchangeRate = apps.get_model('trackshop', 'ExchangeRate')
    Shop = apps.get_model('accounts', 'Shop')

    # 1️⃣ Shop SYSTEM
    system_shop, _ = Shop.objects.get_or_create(
        name='SYSTEM',
        defaults={
            'is_system': True,
            'owner_id': None,
            'default_currency_id': None,
        }
    )

    today = now().date()

    # 2️⃣ Devises
    usd_currency, _ = Currency.objects.get_or_create(
        code='USD',
        defaults={'name': 'Dollar US', 'symbol': '$'}
    )

    cdf_currency, _ = Currency.objects.get_or_create(
        code='CDF',
        defaults={'name': 'Franc Congolais', 'symbol': 'FC'}
    )

    # 3️⃣ Taux de change (⚠️ UNIQUEMENT *_id)
    ExchangeRate.objects.get_or_create(
        shop_id=system_shop.id,
        from_currency_id=usd_currency.id,
        to_currency_id=usd_currency.id,
        date=today,
        defaults={'rate': 1.0}
    )

    ExchangeRate.objects.get_or_create(
        shop_id=system_shop.id,
        from_currency_id=cdf_currency.id,
        to_currency_id=cdf_currency.id,
        date=today,
        defaults={'rate': 1.0}
    )

    ExchangeRate.objects.get_or_create(
        shop_id=system_shop.id,
        from_currency_id=usd_currency.id,
        to_currency_id=cdf_currency.id,
        date=today,
        defaults={'rate': 2000.0}
    )

    ExchangeRate.objects.get_or_create(
        shop_id=system_shop.id,
        from_currency_id=cdf_currency.id,
        to_currency_id=usd_currency.id,
        date=today,
        defaults={'rate': 1 / 2000.0}
    )


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('trackshop', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_currency),
    ]