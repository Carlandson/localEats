# Generated by Django 4.2.2 on 2024-11-11 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0020_alter_kitchen_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='kitchen',
            name='font_body',
            field=models.CharField(default='Inter', max_length=50),
        ),
        migrations.AddField(
            model_name='kitchen',
            name='font_heading',
            field=models.CharField(default='Inter', max_length=50),
        ),
        migrations.AddField(
            model_name='kitchen',
            name='hero_style',
            field=models.CharField(choices=[('image-full', 'Full Screen Image'), ('split', 'Split Layout'), ('minimal', 'Minimal Text')], default='minimal', max_length=20),
        ),
        migrations.AddField(
            model_name='kitchen',
            name='menu_style',
            field=models.CharField(choices=[('grid', 'Grid Layout'), ('classic', 'Classic List'), ('cards', 'Card Layout')], default='classic', max_length=20),
        ),
        migrations.AddField(
            model_name='kitchen',
            name='navigation_style',
            field=models.CharField(choices=[('minimal', 'Minimal Navigation'), ('centered', 'Centered Navigation'), ('split', 'Split Navigation')], default='minimal', max_length=20),
        ),
        migrations.AddField(
            model_name='kitchen',
            name='primary_color',
            field=models.CharField(default='#4F46E5', max_length=7),
        ),
        migrations.AddField(
            model_name='kitchen',
            name='secondary_color',
            field=models.CharField(default='#1F2937', max_length=7),
        ),
        migrations.AddField(
            model_name='kitchen',
            name='show_gallery',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='kitchen',
            name='show_hours',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='kitchen',
            name='show_map',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='kitchen',
            name='show_social_feed',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='kitchen',
            name='show_testimonials',
            field=models.BooleanField(default=True),
        ),
    ]