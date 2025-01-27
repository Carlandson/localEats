# Generated by Django 5.0 on 2025-01-21 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0034_service_featured_homepage_newsfeed_newspost_comment_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='affiliates',
            field=models.ManyToManyField(blank=True, related_name='affiliated_with', to='restaurants.business'),
        ),
    ]