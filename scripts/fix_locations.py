import os
import django
from django.utils.text import slugify

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.models_app.models import County, LocationGroup, Location

def setup_locations():
    # Create County
    nairobi, _ = County.objects.get_or_create(name='Nairobi', defaults={'slug': 'nairobi'})
    
    # Create Group
    main_group, _ = LocationGroup.objects.get_or_create(
        name='Nairobi Areas', 
        county=nairobi,
        defaults={'slug': 'nairobi-areas'}
    )
    
    # Update existing locations to belong to this group
    locations = Location.objects.all()
    for loc in locations:
        loc.group = main_group
        loc.save()
        print(f"Associated {loc.name} with {main_group.name}")

if __name__ == "__main__":
    setup_locations()
