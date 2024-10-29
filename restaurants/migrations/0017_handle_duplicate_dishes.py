from django.db import migrations

def handle_duplicates(apps, schema_editor):
    Dish = apps.get_model('restaurants', 'Dish')
    
    # Get all dishes grouped by course and name
    from django.db.models import Count
    duplicates = Dish.objects.values('course', 'name').annotate(
        count=Count('id')).filter(count__gt=1)
    
    # For each set of duplicates
    for dup in duplicates:
        dishes = Dish.objects.filter(
            course_id=dup['course'], 
            name=dup['name']
        ).order_by('id')
        
        for i, dish in enumerate(dishes[1:], 1):
            dish.name = f"{dish.name} ({i})"
            dish.save()

def reverse_func(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0016_remove_dish_image_url_dish_image'),
    ]

    operations = [
        migrations.RunPython(handle_duplicates, reverse_func),
    ]