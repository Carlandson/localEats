from django.db import migrations, models

def combine_fonts(apps, schema_editor):
    Business = apps.get_model('restaurants', 'Business')
    for business in Business.objects.all():
        # Use heading font as the main font, or body font as fallback
        business.main_font = business.font_heading or business.font_body or 'Arial, sans-serif'
        business.save()

def reverse_fonts(apps, schema_editor):
    Business = apps.get_model('restaurants', 'Business')
    for business in Business.objects.all():
        business.font_heading = business.main_font
        business.font_body = business.main_font
        business.save()

class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0010_subpage_font_body_subpage_font_heading'),  # Replace with your last migration
    ]

    operations = [
        # Add the new field
        migrations.AddField(
            model_name='Business',
            name='main_font',
            field=models.CharField(max_length=50, default='Arial, sans-serif'),
        ),
        # Run the data migration
        migrations.RunPython(combine_fonts, reverse_fonts),
        # Remove the old fields
        migrations.RemoveField(
            model_name='Business',
            name='font_heading',
        ),
        migrations.RemoveField(
            model_name='Business',
            name='font_body',
        ),
    ]