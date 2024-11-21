# Generated by Django 4.2.2 on 2024-11-20 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0012_subpage_hero_font_subpage_hero_heading_size_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subpage',
            old_name='hero_font',
            new_name='hero_heading_font',
        ),
        migrations.AddField(
            model_name='subpage',
            name='hero_subheading_font',
            field=models.CharField(default='Inter', max_length=50),
        ),
    ]
