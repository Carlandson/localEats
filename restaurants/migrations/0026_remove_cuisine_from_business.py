from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0025_transfer_cuisine_to_menu'),  # Make sure this matches your previous migration
    ]

    operations = [
        migrations.RemoveField(
            model_name='business',
            name='cuisine',
        ),
    ]