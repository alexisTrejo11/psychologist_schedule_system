# Generated by Django 5.1.2 on 2025-04-21 01:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_payment_deleted_at_payment_paid_to'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='paid_at',
            field=models.DateTimeField(null=True),
        ),
    ]
