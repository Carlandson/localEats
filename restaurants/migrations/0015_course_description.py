# Generated by Django 4.2.2 on 2024-10-28 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0014_alter_subpage_unique_together_remove_event_kitchen_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]