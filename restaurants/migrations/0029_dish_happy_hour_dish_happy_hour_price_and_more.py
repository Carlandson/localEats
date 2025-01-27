# Generated by Django 5.0 on 2025-01-16 17:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0028_auto_20250113_1210'),
    ]

    operations = [
        migrations.AddField(
            model_name='dish',
            name='happy_hour',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='dish',
            name='happy_hour_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
        ),
        migrations.AddField(
            model_name='dish',
            name='special_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
        ),
        migrations.AddField(
            model_name='specialspage',
            name='happy_hour_days',
            field=models.CharField(blank=True, help_text="Comma-separated days, e.g., 'Mon,Tue,Wed'", max_length=100),
        ),
        migrations.AddField(
            model_name='specialspage',
            name='happy_hour_end',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='specialspage',
            name='happy_hour_start',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='ServicesPage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('subpage', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='services_content', to='restaurants.subpage')),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='service_images/')),
                ('services_page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', to='restaurants.servicespage')),
            ],
        ),
        migrations.CreateModel(
            name='DailySpecial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.IntegerField(choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')])),
                ('is_active', models.BooleanField(default=True)),
                ('dishes', models.ManyToManyField(limit_choices_to={'is_special': True}, to='restaurants.dish')),
                ('specials_page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_specials', to='restaurants.specialspage')),
            ],
            options={
                'ordering': ['day_of_week'],
                'unique_together': {('specials_page', 'day_of_week')},
            },
        ),
    ]
