import json
import geopy.distance
import logging
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from .models import Kitchen, MenuCourse, Dish, CuisineCategory
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from google.auth.exceptions import RefreshError
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import google_auth_httplib2
import httplib2
from allauth.socialaccount.models import SocialAccount
from google.oauth2.credentials import Credentials
from django.core.mail import send_mail
from django.conf import settings
from .forms import RestaurantCreateForm, DishSubmit, CustomSignupView
import googlemaps

User = get_user_model()
logger = logging.getLogger(__name__)

custom_signup = CustomSignupView.as_view()

def some_view(request):
       send_mail(
           'Test Subject',
           'Test message.',
           settings.DEFAULT_FROM_EMAIL,
           ['to@example.com'],
           fail_silently=False,
       )

import logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError
import google_auth_httplib2
import httplib2
import json

logger = logging.getLogger(__name__)

@login_required
def fetch_business_info(request):
    try:
        social_account = SocialAccount.objects.get(user=request.user, provider='google')
        social_token = social_account.socialtoken_set.first()
        
        if not social_token:
            logger.warning("No Google token found for user %s", request.user.username)
            messages.error(request, 'No Google token found. Please reconnect your account.')
            return redirect('some_google_auth_view')
        
        access_token = social_token.token
        credentials = Credentials(token=access_token)
        
        # Create an authorized HTTP object
        http = google_auth_httplib2.AuthorizedHttp(credentials, http=httplib2.Http())
        
        try:
            logger.info("Attempting to build Google My Business API service...")
            service = build('mybusinessaccountmanagement', 'v1', http=http, cache_discovery=False)
            logger.info("Successfully built Google My Business API service")
       
            try:
                # You need to list accounts first
                accounts = service.accounts().list().execute()
                logger.debug("Accounts response: %s", json.dumps(accounts, indent=2))
                
                if 'accounts' in accounts and accounts['accounts']:
                    account = accounts['accounts'][0]
                    account_name = account['name']  # This will be 'accounts/{account_id}'
                    
                    # Use the account_name to list all locations for the account
                    service = build('mybusinessbusinessinformation', 'v1', http=http, cache_discovery=False)
                    locations = service.accounts().locations().list(parent=account_name).execute()
                    logger.debug("Locations response: %s", json.dumps(locations, indent=2))
                    
                    if 'locations' in locations and locations['locations']:
                        location = locations['locations'][0]
                        # Fetch detailed information for the first location
                        location_name = location['name']
                        location_details = service.accounts().locations().get(name=location_name).execute()
                        logger.debug("Location details: %s", json.dumps(location_details, indent=2))
                        
                        return render(request, 'create.html', {'business_info': location_details})
                    else:
                        logger.warning("No business locations found for user %s", request.user.username)
                        messages.warning(request, 'No business locations found for this Google account. You may need to create a Google My Business listing first.')
                        return redirect('create')  # or wherever you want to redirect
                
                else:
                    logger.warning("No Google My Business accounts found for user %s", request.user.username)
                    messages.warning(request, 'No Google My Business accounts found for this user.')
                    return redirect('create')
            
            except HttpError as api_error:
                if api_error.resp.status == 403:
                    logger.warning("Permission denied. The user might not have any business listings. User: %s", request.user.username)
                    messages.warning(request, 'Unable to access business information. You may not have any Google My Business listings, or you may need to grant additional permissions.')
                else:
                    logger.error("API error: %s", api_error, exc_info=True)
                    messages.error(request, f'Error fetching business info: {api_error.reason}')
            
        except HttpError as error:
            logger.error("An HTTP error occurred: %s", error, exc_info=True)
            messages.error(request, f'Error accessing Google My Business API: {error}')
        except RefreshError as refresh_error:
            logger.error("Token refresh error: %s", refresh_error, exc_info=True)
            messages.error(request, 'Your Google token has expired. Please reconnect your account.')
            return redirect('some_google_auth_view')
        except Exception as e:
            logger.error("Error building API service: %s", str(e), exc_info=True)
            messages.error(request, f'Error accessing Google My Business API: {str(e)}')
    
    except SocialAccount.DoesNotExist:
        logger.error("SocialAccount does not exist for user %s", request.user.username)
        messages.error(request, 'Google account not connected.')
    except Exception as e:
        logger.error("Unexpected error: %s", str(e), exc_info=True)
        messages.error(request, f'Error fetching business info: {str(e)}')
    
    return redirect('create')


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
            new_restaurant = form.save(commit=False)
            new_restaurant.owner = user

            # Combine address components for geocoding
            full_address = f"{new_restaurant.address}, {new_restaurant.city}, {new_restaurant.state} {new_restaurant.zip_code}"

            try:
                # Geocode the address
                geocode_result = gmaps.geocode(full_address)

                if geocode_result:
                    location = geocode_result[0]['geometry']['location']
                    formatted_address = geocode_result[0]['formatted_address']
                    coordinates = f"{location['lat']},{location['lng']}"

                    if Kitchen.verified_business_exists(formatted_address):
                        raise ValidationError("A verified business already exists at this address.")
                    
                    new_restaurant.address = formatted_address

                    new_restaurant.save()

                    messages.success(request, 'Restaurant created successfully!')
                    return redirect(reverse('eatery', kwargs={'eatery': new_restaurant.subdirectory}))
                else:
                    messages.error(request, 'Unable to validate the address. Please check and try again.')
            except Exception as e:
                logger.error(f"Error creating restaurant: {str(e)}", exc_info=True)
                messages.error(request, f'An error occurred: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
            logger.error(f"Form validation errors: {form.errors}")

        context = {
            "create": form,
            "google_maps_api_key": settings.GOOGLE_MAPS_API_KEY
        }
        return render(request, "create.html", context)

def eatery(request, eatery):
    restaurant = get_object_or_404(Kitchen, subdirectory=eatery)
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