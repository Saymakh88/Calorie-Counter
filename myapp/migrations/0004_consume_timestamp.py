# Generated by Django 5.1.7 on 2025-07-15 13:54

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_alter_consume_food_consumed'),
    ]

    operations = [
        migrations.AddField(
            model_name='consume',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
