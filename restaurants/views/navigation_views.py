# Django core imports
from django.http import JsonResponse

# Local imports
from ..models import Business

def search(request, position, distance):
    if request.method != "GET":
        return JsonResponse({"error" : "GET request required."}, status=400)
    if distance == "Walk":
        distance_lat = .03
        distance_lon = .04
    if distance == "Bike":
        distance_lat = .075
        distance_lon = .1
    if distance == "Drive":
        distance_lat = .225
        distance_lon = .3
    latitude = position.split(", ")[0]
    latitude = float(latitude)
    longitude = position.split(", ")[1]
    longitude = float(longitude)
    distance_plus_lat = latitude + distance_lat
    distance_minus_lat = latitude - distance_lat
    distance_plus_lon = longitude + distance_lon
    distance_minus_lon = longitude - distance_lon
    business_list = Business.objects.all()
    businesss_nearby = []
    test_dict = []
    for business in business_list:
        coordinates = str(business.geolocation)
        business_latitude = float(coordinates.split(",")[0])
        business_longitude = float(coordinates.split(",")[1])
        if distance_plus_lat > business_latitude > distance_minus_lat and distance_plus_lon > business_longitude > distance_minus_lon:
            between_locations = round(geopy.distance.distance(position, coordinates).miles, 2)
            businesss_nearby.append(business)
            e = {
                "name": business.business_name,
                "address": business.address,
                "city": business.city,
                "state": business.state,
                "description": business.description,
                "between": between_locations,
                "cuisine": business.menus.first().cuisine.first().cuisine
            }
            test_dict.append(e)
    return JsonResponse([localbusiness for localbusiness in test_dict], safe=False)

def filter(request, place):
    if request.method != "GET":
        return JsonResponse({"error" : "GET request required."}, status=400)
    location_businesss = Business.objects.filter(city__icontains = place)
    return JsonResponse([localEatery.serialize() for localEatery in location_businesss], safe=False)