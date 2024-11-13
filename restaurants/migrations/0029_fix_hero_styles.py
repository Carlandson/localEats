from django.db import migrations

def fix_hero_styles(apps, schema_editor):
    Kitchen = apps.get_model('restaurants', 'Kitchen')
    # Update any navigation styles that were incorrectly saved as hero styles
    Kitchen.objects.filter(hero_style='minimal').update(hero_style='image-full')
    Kitchen.objects.filter(hero_style='centered').update(hero_style='image-full')
    Kitchen.objects.filter(hero_style='split').update(hero_style='image-full')
    Kitchen.objects.filter(hero_style='fullscreen').update(hero_style='image-full')

class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0028_update_hero_styles'),  # Replace with your last migration
    ]

    operations = [
        migrations.RunPython(fix_hero_styles),
    ]