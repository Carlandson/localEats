# Generated by Django 4.2.2 on 2024-10-23 20:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0009_kitchen_subidrectory'),
    ]

    operations = [
        migrations.RenameField(
            model_name='kitchen',
            old_name='subidrectory',
            new_name='subdirectory',
        ),
    ]