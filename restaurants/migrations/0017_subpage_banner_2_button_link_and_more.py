# Generated by Django 4.2.2 on 2024-12-04 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0016_subpage_banner_2_heading_color_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='subpage',
            name='banner_2_button_link',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='subpage',
            name='banner_2_button_text',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='subpage',
            name='banner_2_text_align',
            field=models.CharField(choices=[('left', 'Left'), ('center', 'Center'), ('right', 'Right')], default='left', max_length=10),
        ),
        migrations.AddField(
            model_name='subpage',
            name='banner_3_button_link',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='subpage',
            name='banner_3_button_text',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='subpage',
            name='banner_3_text_align',
            field=models.CharField(choices=[('left', 'Left'), ('center', 'Center'), ('right', 'Right')], default='left', max_length=10),
        ),
    ]
