import json
import geopy.distance

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django import forms
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.forms import TextInput, ModelForm, Textarea
from geopy.geocoders import Nominatim
from .models import Kitchen, MenuCourse, Dish, CuisineCategory
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from allauth.account.utils import perform_login
from allauth.account.models import EmailAddress
from allauth.account.utils import perform_login
from allauth.account.forms import LoginForm
from django.contrib.auth import logout as auth_logout
from allauth.account.views import SignupView
from .forms import CustomSignupForm
from django.core.mail import send_mail
from django.conf import settings
from .forms import RestaurantCreateForm, DishSubmit, CustomSignupForm, CustomSignupView
import googlemaps

User = get_user_model()

custom_signup = CustomSignupView.as_view()

def some_view(request):
       send_mail(
           'Test Subject',
           'Test message.',
           settings.DEFAULT_FROM_EMAIL,
           ['to@example.com'],
           fail_silently=False,
       )

def index(request): 
    kitchen_list = Kitchen.objects.all().order_by('-created')
    paginator = Paginator(kitchen_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = {
            'kitchens': [
                {
                    'name': kitchen.restaurant_name,
                    'city': kitchen.city,
                    'state': kitchen.state,
                    'cuisine': str(kitchen.cuisine),
                    'created': kitchen.created.strftime('%B %d, %Y'),
                    'url': reverse('eatery', args=[kitchen.restaurant_name])
                } for kitchen in page_obj
            ],
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'num_pages': paginator.num_pages,
            'current_page': page_obj.number
        }
        return JsonResponse(data)

    return render(request, 'index.html', {'page_obj': page_obj})

def custom_logout(request):
    logout(request)
    return JsonResponse({'success': True})


def profile(request):
    restaurant_list = Kitchen.objects.all()
    owners_restaurants = []
    owner_check = False
    for restaurant in restaurant_list:
        if restaurant.owner == request.user:
            owners_restaurants.append(restaurant)
            owner_check = True
    return render(request, "profile.html", {"profile": profile, "owner_check" : owner_check, "owners_restaurants" : owners_restaurants})

def about(request):
    return render(request, "about.html")

@login_required
def create(request):
    user = request.user
    gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

    if request.method == "GET":
        context = {
            "create": RestaurantCreateForm(),
            "owner": user,
            "google_maps_api_key": settings.GOOGLE_MAPS_API_KEY
        }
        return render(request, "create.html", context)

    if request.method == "POST":
        form = RestaurantCreateForm(request.POST)
        if form.is_valid():
            restaurant_name = form.cleaned_data['restaurant_name']
            address = form.cleaned_data['address']
            description = form.cleaned_data['description']
            state = form.cleaned_data['state']
            cuisine = form.cleaned_data['cuisine']
            country = form.cleaned_data['country']
            city = form.cleaned_data['city']
            phone_number = form.cleaned_data['phone_number']

            # Combine address components for geocoding
            full_address = f"{address}, {city}, {state}, {country}"

            try:
                # Geocode the address
                geocode_result = gmaps.geocode(full_address)

                if geocode_result:
                    location = geocode_result[0]['geometry']['location']
                    formatted_address = geocode_result[0]['formatted_address']
                    coordinates = f"{location['lat']},{location['lng']}"

                    new_restaurant = Kitchen(
                        owner=user,
                        phone_number=phone_number,
                        city=city,
                        restaurant_name=restaurant_name,
                        address=formatted_address,
                        description=description,
                        state=state,
                        country=country,
                        cuisine=cuisine,
                        geolocation=coordinates
                    )
                    new_restaurant.save()

                    messages.success(request, 'Restaurant created successfully!')
                    return redirect(reverse('eatery', kwargs={'eatery': new_restaurant.restaurant_name}))
                else:
                    messages.error(request, 'Unable to validate the address. Please check and try again.')
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors in the form.')
        context = {
            "create": form,
            "google_maps_api_key": settings.GOOGLE_MAPS_API_KEY
        }
        return render(request, "create.html", context)

def eatery(request, eatery):
    restaurant = get_object_or_404(Kitchen, restaurant_name=eatery)
    courses = MenuCourse.objects.all()
    dishes = Dish.objects.filter(recipe_owner=restaurant)
    restaurant_courses = restaurant.courses.all()

    context = {
        "eatery": eatery,
        "restaurant_details": restaurant,
        "courses": restaurant_courses,
        "dishes": dishes,
        "course_list": courses,
        "owner": request.user == restaurant.owner,
        "is_verified": restaurant.is_verified,
    }

    if request.method != "GET":
        return JsonResponse({"error": "GET request required."}, status=400)

    if not restaurant.is_verified and request.user != restaurant.owner:
        return render(request, "restaurant_under_construction.html", context)

    return render(request, "eatery.html", context)


@login_required
def new_dish(request, kitchen_name):
    if request.method == "GET":
        return render(request, "newdish.html", {"new_dish" : DishSubmit()})
    if request.method == "POST":
        form = Dish(request.POST)
        user = request.user
        if form.is_valid():
            name = form.cleaned_data["name"]
            price = form.cleaned_data["price"]
            recipe_owner = kitchen_name
            image_url = form.cleaned_data["image_url"]
            course = form.cleaned_data["course"]
            description = form.cleaned_data["description"]
        else:
            print(form.errors)
            return render(request, "newdish.html", {"new_dish" : DishSubmit()})
        new = Dish(name=name, price=price, image_url=image_url, course=course, description=description, recipe_owner=recipe_owner)
        new.save()
        messages.add_message(request, messages.INFO, f"'{name}' successfully added to menu")
        return HttpResponseRedirect(reverse('eatery', kwargs={"eatery": kitchen_name}))

@csrf_exempt
@login_required
def add_course(request, dishData, eatery):
    course_add = MenuCourse.objects.get(course_list=dishData)
    try:
        current_restaurant = Kitchen.objects.get(restaurant_name = eatery)
    except Kitchen.DoesNotExist:
        return JsonResponse({"error": "kitchen does not exist."}, status=404)
    if request.method == "POST":
        current_restaurant.courses.add(course_add)
        current_restaurant.save()
        return JsonResponse({"message": "course added"},status=201)
    else:
        return JsonResponse({"error": "GET request required."}, status=400)

@csrf_exempt
@login_required
def add_dish(request, eatery):
    if request.method != "POST":
        return JsonResponse({"error" : "POST request required."}, status=400)
    data = json.loads(request.body)
    user = request.user
    name = data.get("name", "")
    description = data.get("description", "")
    price = data.get("price", "")
    image_url = data.get("image_url", "")
    course = data.get("course", "")
    dish_course = MenuCourse.objects.get(course_list=course)
    eatery = Kitchen.objects.get(restaurant_name=eatery)
    new_dish = Dish(
        recipe_owner = eatery,
        name = name,
        description = description,
        price = price,
        image_url = image_url,
        course = dish_course,
    )
    new_dish.save()
    return JsonResponse({"message": "Dish added"}, status=201)

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
    kitchen_list = Kitchen.objects.all()
    kitchens_nearby = []
    test_dict = []
    for eatery in kitchen_list:
        coordinates = str(eatery.geolocation)
        eatery_latitude = float(coordinates.split(",")[0])
        eatery_longitude = float(coordinates.split(",")[1])
        if distance_plus_lat > eatery_latitude > distance_minus_lat and distance_plus_lon > eatery_longitude > distance_minus_lon:
            between_locations = round(geopy.distance.distance(position, coordinates).miles, 2)
            kitchens_nearby.append(eatery)
            e = {
                "eatery": eatery.cuisine.cuisine,
                "name": eatery.restaurant_name,
                "address": eatery.address,
                "city": eatery.city,
                "state": eatery.state,
                "description": eatery.description,
                "between": between_locations,
                "cuisine": eatery.cuisine.cuisine
            }
            test_dict.append(e)
    return JsonResponse([localKitchen for localKitchen in test_dict], safe=False)

def filter(request, place):
    if request.method != "GET":
        return JsonResponse({"error" : "GET request required."}, status=400)
    location_kitchens = Kitchen.objects.filter(city__icontains = place)
    return JsonResponse([localEatery.serialize() for localEatery in location_kitchens], safe=False)

@csrf_exempt
@login_required
def edit_dish(request, dishid):
    try:
        item = Dish.objects.get(id = dishid)
    except Dish.DoesNotExist:
        return JsonResponse({"error": "dish does not exist."}, status=404)
    if request.method == "GET":
        return JsonResponse(item.serialize())
    if request.method == "POST":
        data = json.loads(request.body)
        description = data.get("description", "")
        name = data.get("name", "")
        price = data.get("price", "")
        image = data.get("image", "")
        item.description = description
        item.name = name
        item.price = price
        item.image_url = image
        item.save()
        return JsonResponse({"message": "post successfully edited!"}, status=201)
    else:
        return JsonResponse({"error": "GET or POST request required."}, status=400)

@csrf_exempt
@login_required
def delete_dish(request, dishid):
    try:
        item = Dish.objects.get(id = dishid)
    except Dish.DoesNotExist:
        return JsonResponse({"error": "dish does not exist."}, status=404)
    if request.method != "GET":
        return JsonResponse({"error" : "GET request required."}, status=400)
    item.delete()
    return JsonResponse({"message": "dish deleted"}, status=201)

@csrf_exempt
@login_required
def delete_course(request, eatery, course):
    if request.method != "GET":
        return JsonResponse({"error" : "GET request required."}, status=400)
    current_course = MenuCourse.objects.get(course_list = course)
    current_kitchen = Kitchen.objects.get(restaurant_name = eatery, owner = request.user)
    current_kitchen.courses.remove(current_course)
    return JsonResponse({"message": "course deleted"}, status=201)


def get_kitchen(request, kitchen_id):
    try:
        kitchen_obj = Kitchen.objects.get(id=kitchen_id)
        return JsonResponse(kitchen_obj.serialize())
    except Kitchen.DoesNotExist:
        return JsonResponse({"error": "Kitchen not found"}, status=404)

def get_dish(request, dish_id):
    try:
        dish_obj = Dish.objects.get(id=dish_id)
        return JsonResponse(dish_obj.serialize())
    except Dish.DoesNotExist:
        return JsonResponse({"error": "Dish not found"}, status=404)

def get_cuisine_categories(request):
    categories = CuisineCategory.objects.all()
    return JsonResponse([category.serialize() for category in categories], safe=False)