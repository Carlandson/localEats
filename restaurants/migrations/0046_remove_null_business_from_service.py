from django.db import migrations, models

def verify_no_null_business(apps, schema_editor):
    Service = apps.get_model('restaurants', 'Service')
    if Service.objects.filter(business__isnull=True).exists():
        raise Exception("There are services with null business values")

class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0045_service_business'),  # Replace with your last migration
    ]

    operations = [
        # First verify no null values exist
        migrations.RunPython(verify_no_null_business),
        
        # Then modify the field
        migrations.AlterField(
            model_name='service',
            name='business',
            field=models.ForeignKey(
                on_delete=models.CASCADE,
                related_name='services',
                to='restaurants.business'
            ),
        ),
    ]