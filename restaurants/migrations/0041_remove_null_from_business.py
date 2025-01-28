from django.db import migrations, models

def verify_no_null_business(apps, schema_editor):
    Product = apps.get_model('restaurants', 'Product')
    if Product.objects.filter(business__isnull=True).exists():
        raise Exception("There are products with null business values")

class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0040_alter_dailyspecial_options_and_more'),  # Replace with your previous migration
    ]

    operations = [
        # First verify no null values exist
        migrations.RunPython(verify_no_null_business),
        
        # Then modify the field
        migrations.AlterField(
            model_name='product',
            name='business',
            field=models.ForeignKey(
                on_delete=models.CASCADE,
                related_name='products',
                to='restaurants.business'
            ),
        ),
    ]