# Generated by Django 5.0.4 on 2024-07-03 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='approved',
            field=models.BooleanField(default=False),
        ),
    ]
