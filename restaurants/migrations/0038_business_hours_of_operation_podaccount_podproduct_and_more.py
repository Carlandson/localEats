# Generated by Django 5.0 on 2025-01-24 17:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0037_alter_aboutuspage_options_aboutuspage_core_values_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='hours_of_operation',
            field=models.TextField(blank=True, default='', max_length=200),
        ),
        migrations.CreateModel(
            name='PODAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider', models.CharField(choices=[('PRINTFUL', 'Printful'), ('PRINTIFY', 'Printify')], max_length=50)),
                ('api_key', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('business', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='restaurants.business')),
            ],
        ),
        migrations.CreateModel(
            name='PODProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider_product_id', models.CharField(max_length=255)),
                ('title', models.CharField(max_length=255)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('design_data', models.JSONField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restaurants.business')),
                ('pod_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restaurants.podaccount')),
            ],
        ),
        migrations.AddIndex(
            model_name='podaccount',
            index=models.Index(fields=['provider'], name='restaurants_provide_dbd575_idx'),
        ),
        migrations.AddIndex(
            model_name='podproduct',
            index=models.Index(fields=['provider_product_id'], name='restaurants_provide_071b65_idx'),
        ),
        migrations.AddIndex(
            model_name='podproduct',
            index=models.Index(fields=['business', 'is_active'], name='restaurants_busines_7d6631_idx'),
        ),
    ]