from django.db import migrations

def update_hero_styles(apps, schema_editor):
    Kitchen = apps.get_model('restaurants', 'Kitchen')
    # Update any invalid hero styles to the default
    Kitchen.objects.filter(hero_style__in=['centered', 'split', 'fullscreen']).update(hero_style='image-full')

class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0027_alter_kitchen_hero_style'),  # Replace with your last migration
    ]

    operations = [
        migrations.RunPython(update_hero_styles),
    ]