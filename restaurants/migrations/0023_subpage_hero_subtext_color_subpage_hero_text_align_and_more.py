# Generated by Django 4.2.2 on 2024-11-13 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0022_subpage_hero_button_link_subpage_hero_button_text_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='subpage',
            name='hero_subtext_color',
            field=models.CharField(default='#6B7280', max_length=7),
        ),
        migrations.AddField(
            model_name='subpage',
            name='hero_text_align',
            field=models.CharField(choices=[('left', 'Left'), ('center', 'Center')], default='left', max_length=10),
        ),
        migrations.AddField(
            model_name='subpage',
            name='hero_text_color',
            field=models.CharField(default='#000000', max_length=7),
        ),
    ]