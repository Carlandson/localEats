# Generated by Django 5.0 on 2025-01-28 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0042_eventspage_show_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='productspage',
            name='show_description',
            field=models.BooleanField(default=False),
        ),
    ]
