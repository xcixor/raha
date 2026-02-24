from django.shortcuts import render
from ..models import Location, County

def get_nearby_locations(request):
    primary_location_id = request.GET.get('primary_location_id') or request.GET.get('primary_location')
    if not primary_location_id:
        return render(request, 'models_app/partials/nearby_locations_options.html', {'locations': []})

    try:
        primary_location = Location.objects.get(id=primary_location_id)
        if primary_location.group:
            # Get all locations in the same group, excluding the primary one
            nearby = Location.objects.filter(group=primary_location.group).exclude(id=primary_location.id)
        else:
            nearby = []
    except Location.DoesNotExist:
        nearby = []

    return render(request, 'models_app/partials/nearby_locations_options.html', {'locations': nearby})

def filter_locations_by_county(request):
    county_slug = request.GET.get('county')
    try:
        county = County.objects.get(slug=county_slug)
        locations = Location.objects.filter(group__county=county).order_by('name')
    except (County.DoesNotExist, ValueError):
        locations = []
        county = None
        
    return render(request, 'models_app/partials/location_row_items.html', {
        'locations': locations,
        'active_county': county,
        'active_location_slug': 'all'
    })
