# Generated by Django 4.2.2 on 2024-11-18 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0005_subpage_show_hero_heading_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='subpage',
            name='primary_color',
            field=models.CharField(default='#4F46E5', max_length=7),
        ),
        migrations.AddField(
            model_name='subpage',
            name='secondary_color',
            field=models.CharField(default='#1F2937', max_length=7),
        ),
    ]
