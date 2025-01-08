from django.db import migrations, models

def transfer_cuisine_to_menu(apps, schema_editor):
    Business = apps.get_model('restaurants', 'Business')
    Menu = apps.get_model('restaurants', 'Menu')
    
    # For each business
    for business in Business.objects.all():
        # Check if business has any cuisines
        cuisines = business.cuisine.all()
        if not cuisines.exists():
            continue
            
        # Get all menus for this business
        menus = Menu.objects.filter(business=business)
        if not menus.exists():
            continue
            
        # Add cuisines to each menu
        for menu in menus:
            menu.cuisine.add(*cuisines)

def reverse_cuisine_transfer(apps, schema_editor):
    Business = apps.get_model('restaurants', 'Business')
    Menu = apps.get_model('restaurants', 'Menu')
    
    # For each business
    for business in Business.objects.all():
        # Get first menu's cuisines (if menu exists)
        menu = Menu.objects.filter(business=business).first()
        if menu and menu.cuisine.exists():
            cuisines = menu.cuisine.all()
            business.cuisine.add(*cuisines)

class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0024_alter_subpage_page_type'),  # Replace with your actual previous migration
    ]

    operations = [
        migrations.AddField(
            model_name='menu',
            name='cuisine',
            field=models.ManyToManyField(blank=True, related_name='menu_cuisines', to='restaurants.CuisineCategory'),
        ),
        migrations.AlterField(
            model_name='business',
            name='cuisine',
            field=models.ManyToManyField(blank=True, related_name='business_cuisines', to='restaurants.CuisineCategory'),
        ),
        migrations.RunPython(transfer_cuisine_to_menu, reverse_cuisine_transfer),
    ]