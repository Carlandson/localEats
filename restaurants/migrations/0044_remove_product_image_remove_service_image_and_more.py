# Generated by Django 5.0 on 2025-01-29 19:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0043_productspage_show_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='image',
        ),
        migrations.RemoveField(
            model_name='service',
            name='image',
        ),
        migrations.AddField(
            model_name='servicespage',
            name='show_description',
            field=models.BooleanField(default=False),
        ),
    ]
