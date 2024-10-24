# Generated by Django 4.2.2 on 2024-10-16 18:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
import django_google_maps.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CuisineCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cuisine', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='MenuCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_list', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Kitchen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('restaurant_name', models.CharField(max_length=64)),
                ('address', django_google_maps.fields.AddressField(max_length=200)),
                ('geolocation', django_google_maps.fields.GeoLocationField(blank=True, max_length=100)),
                ('city', models.CharField(max_length=64)),
                ('state', models.CharField(max_length=64)),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('description', models.TextField(default='', max_length=200)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('phone_number', models.IntegerField(blank=True)),
                ('courses', models.ManyToManyField(blank=True, related_name='kitchen_courses', to='restaurants.menucourse')),
                ('cuisine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cuisines', to='restaurants.cuisinecategory')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owner', to=settings.AUTH_USER_MODEL)),
                ('user_favorite', models.ManyToManyField(blank=True, related_name='regular', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Dish',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=6)),
                ('name', models.CharField(max_length=64)),
                ('image_url', models.ImageField(upload_to='images')),
                ('description', models.TextField(default='', max_length=200)),
                ('date_added', models.DateField(auto_now=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='restaurants.menucourse')),
                ('favorites', models.ManyToManyField(blank=True, related_name='user_favorite', to=settings.AUTH_USER_MODEL)),
                ('recipe_owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='kitchen', to='restaurants.kitchen')),
            ],
        ),
    ]
