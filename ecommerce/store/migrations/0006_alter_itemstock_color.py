# Generated by Django 5.0.4 on 2024-04-29 20:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemstock',
            name='color',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.color'),
        ),
    ]
