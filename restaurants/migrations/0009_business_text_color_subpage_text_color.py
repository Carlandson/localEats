# Generated by Django 4.2.2 on 2024-11-19 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0008_subpage_hover_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='text_color',
            field=models.CharField(default='#000000', max_length=7),
        ),
        migrations.AddField(
            model_name='subpage',
            name='text_color',
            field=models.CharField(default='#000000', max_length=7),
        ),
    ]
