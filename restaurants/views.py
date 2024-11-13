import json
import geopy.distance
import logging
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound, HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.core.paginator import Paginator
from .models import Image, SubPage, Menu, Course, Dish, AboutUsPage, EventsPage, Event, SpecialsPage, Kitchen, CuisineCategory, SideOption
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from google.auth.exceptions import RefreshError
from googleapiclient.errors import HttpError
from django.views.decorators.csrf import ensure_csrf_cookie
from googleapiclient.discovery import build
import google_auth_httplib2
import httplib2
from allauth.socialaccount.models import SocialAccount
from google.oauth2.credentials import Credentials
from django.core.mail import send_mail
from django.conf import settings
from .forms import RestaurantCreateForm, DishSubmit, CustomSignupView, ImageUploadForm, RestaurantCustomizationForm
from django.contrib.contenttypes.models import ContentType
from django.db.models import Max
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
import base64, uuid
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

def aboutus(request):
    return render(request, "aboutus.html")

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

def get_restaurant_context(restaurant, user, is_preview=False):
    """Helper function to create consistent context for both views"""
    # Get subpage information
    menu_page = SubPage.objects.filter(kitchen=restaurant, page_type='menu').exists()
    about_page = SubPage.objects.filter(kitchen=restaurant, page_type='about').exists()
    events_page = SubPage.objects.filter(kitchen=restaurant, page_type='events').exists()
    specials_page = SubPage.objects.filter(kitchen=restaurant, page_type='specials').exists()
    
    return {
        "eatery": restaurant.subdirectory,
        "restaurant_details": restaurant,
        "owner": user == restaurant.owner,
        "is_verified": restaurant.is_verified,
        "menu_page": menu_page,
        "about_page": about_page,
        "events_page": events_page,
        "specials_page": specials_page,
        "is_preview": is_preview
    }

def eatery(request, eatery):
    restaurant = get_object_or_404(Kitchen, subdirectory=eatery)
    
    if request.method != "GET":
        return JsonResponse({"error": "GET request required."}, status=400)

    # Get or create home subpage
    subpage, created = SubPage.objects.get_or_create(
        kitchen=restaurant,
        page_type='home',
        defaults={
            'title': restaurant.restaurant_name,
            'slug': restaurant.subdirectory,
            'is_published': True
        }
    )

    # Get your existing context
    context = get_restaurant_context(restaurant, request.user)
    
    # Add subpage to context
    context.update({
        'subpage': subpage,
        'is_home': True
    })

    if not restaurant.is_verified and request.user != restaurant.owner:
        return render(request, "restaurant_under_construction.html", context)

    if request.user == restaurant.owner:
        return render(request, "eatery_owner.html", context)
    else:
        return render(request, "visitor_layout.html", context)
    
def create_subpage(request, eatery, page_type):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    restaurant = get_object_or_404(Kitchen, subdirectory=eatery)
    
    # Check if user is owner
    if request.user != restaurant.owner:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    # Create the subpage
    subpage = SubPage.objects.create(
        kitchen=restaurant,
        page_type=page_type,
        title=f"{restaurant.restaurant_name} {page_type.title()}",
        slug=f"{restaurant.subdirectory}-{page_type}",
        is_published=True
    )

    # Create the corresponding page content based on type
    if page_type == 'menu':
        Menu.objects.create(
            kitchen=restaurant,
            name=f"{restaurant.restaurant_name} Menu",
            subpage=subpage
        )
    elif page_type == 'about':
        AboutUsPage.objects.create(
            subpage=subpage,
            content=""
        )
    elif page_type == 'events':
        EventsPage.objects.create(
            subpage=subpage
        )
    elif page_type == 'specials':
        SpecialsPage.objects.create(
            subpage=subpage
        )

    # Redirect to the appropriate page
    return redirect(reverse(page_type, kwargs={'eatery': eatery}))

def menu(request, eatery):
    restaurant = get_object_or_404(Kitchen, subdirectory=eatery)
    menu_subpage = get_object_or_404(SubPage, kitchen=restaurant, page_type='menu')
    menu = get_object_or_404(Menu, subpage=menu_subpage)
    courses = Course.objects.filter(menu=menu).order_by('order')
    dishes = Dish.objects.filter(menu=menu)
    course_options = [
        'Appetizers',
        'Lunch',
        'Entrees',
        'Main Courses',
        'Soup and Salad',
        'Salads',
        'Desserts',
        'Drinks',
        'Specials',
        'Dinner',
        'Breakfast',
        'Brunch',
        'Kids Menu',
        'Beverages',
        'Vegan',
        'Gluten Free',
        'Dairy Free',
        'Nut Free',
        'Halal',
        'Kosher'
    ]
    context = {
        "eatery": eatery,
        "restaurant_details": restaurant,
        "courses": courses,
        "dishes": dishes,
        "course_options": course_options,
        "owner": request.user == restaurant.owner,
        "is_verified": restaurant.is_verified,
    }

    if request.method != "GET":
        return JsonResponse({"error": "GET request required."}, status=400)

    if not restaurant.is_verified and request.user != restaurant.owner:
        return render(request, "restaurant_under_construction.html", context)
    return render(request, "kitchen_subpages/menu.html", context)


def about(request, eatery):
    restaurant = get_object_or_404(Kitchen, subdirectory=eatery)
    about_page = AboutUsPage.objects.filter(kitchen=restaurant)
    context = {
        "about_page": about_page,
        "owner": request.user == restaurant.owner,
    }
    return render(request, "about.html", context)

def specials(request, eatery):
    restaurant = get_object_or_404(Kitchen, subdirectory=eatery)
    specials_page = SpecialsPage.objects.filter(kitchen=restaurant)
    context = {
        "specials_page": specials_page,
        "owner": request.user == restaurant.owner,
    }
    return render(request, "specials.html", context)

def events(request, eatery):
    restaurant = get_object_or_404(Kitchen, subdirectory=eatery)
    events_page = EventsPage.objects.filter(kitchen=restaurant)
    context = {
        "events_page": events_page,
        "owner": request.user == restaurant.owner,
    }
    return render(request, "events.html", context)

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

@ensure_csrf_cookie
def add_course(request, eatery):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    restaurant = get_object_or_404(Kitchen, subdirectory=eatery)
    
    # Check if user is owner
    if request.user != restaurant.owner:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    try:
        data = json.loads(request.body)
        course_name = data.get('course_name')
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    if not course_name:
        return JsonResponse({"error": "Course name is required"}, status=400)

    # Get the menu
    menu_subpage = get_object_or_404(SubPage, kitchen=restaurant, page_type='menu')
    menu = get_object_or_404(Menu, subpage=menu_subpage)

    # Create new course
    highest_order = Course.objects.filter(menu=menu).aggregate(Max('order'))['order__max'] or 0
    course = Course.objects.create(
        menu=menu,
        name=course_name,
        order=highest_order + 1
    )

    return JsonResponse({
        "message": "Course added successfully",
        "course_id": course.id
    })

@csrf_exempt
@login_required
def add_dish(request, eatery):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    try:
        data = json.loads(request.body)
        restaurant = get_object_or_404(Kitchen, subdirectory=eatery)
        
        # Check if user is owner
        if request.user != restaurant.owner:
            return JsonResponse({"error": "Unauthorized"}, status=403)

        # Get the menu
        menu_subpage = get_object_or_404(SubPage, kitchen=restaurant, page_type='menu')
        menu = get_object_or_404(Menu, subpage=menu_subpage)

        # Get or create the course
        course_name = data.get("course", "")
        course = Course.objects.get(menu=menu, name=course_name)

        dish_name = data.get("name", "").strip()
        if Dish.objects.filter(course=course, name__iexact=dish_name).exists():
            return JsonResponse({
                "error": f"A dish with the name '{dish_name}' already exists in the {course_name} course."
            }, status=400)
        
        image_data = data.get('image')
        image = None
        if image_data and 'base64,' in image_data:
            # Split the base64 string
            format, imgstr = image_data.split('base64,')
            # Get the file extension
            ext = format.split('/')[-1].split(';')[0]
            # Generate filename
            filename = f"{restaurant.subdirectory}_{data.get('name')}_{uuid.uuid4().hex[:6]}.{ext}"
            
            # Create ContentFile from base64 data
            image = ContentFile(base64.b64decode(imgstr), name=filename)

        # Create new dish
        new_dish = Dish.objects.create(
            menu=menu,
            name=data.get("name", ""),
            description=data.get("description", ""),
            price=data.get("price", ""),
            image=image,
            course=course
        )

        return JsonResponse({
            "message": "Dish added successfully",
            "dish_id": new_dish.id,
            "image_url": new_dish.image.url if new_dish.image else ""
        }, status=201)

    except Course.DoesNotExist:
        return JsonResponse({
            "error": f"Course '{course_name}' not found"
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            "error": "Invalid JSON"
        }, status=400)
    except IntegrityError:
        return JsonResponse({
            "error": "A dish with this name already exists in your menu."
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "error": str(e)
        }, status=400)

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
def edit_dish(request, eatery, dishid):
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)
    
    try:
        dish = Dish.objects.get(id=dishid)
        restaurant = get_object_or_404(Kitchen, subdirectory=eatery)
        
        # Verify owner
        if request.user != restaurant.owner:
            return JsonResponse({"error": "Unauthorized"}, status=403)
            
        data = json.loads(request.body)
        new_name = data.get('name', '').strip()

        # Check if new name already exists in this course (excluding current dish)
        if new_name.lower() != dish.name.lower() and \
           Dish.objects.filter(course=dish.course, name__iexact=new_name).exists():
            return JsonResponse({
                "error": f"A dish with the name '{new_name}' already exists in the {dish.course.name} course."
            }, status=400)
                
        # Update dish fields
        dish.name = data.get('name', dish.name)
        dish.price = data.get('price', dish.price)
        dish.description = data.get('description', dish.description)

        # Handle image data
        image_data = data.get('image')
        if image_data and 'base64,' in image_data:
            # Split the base64 string
            format, imgstr = image_data.split('base64,')
            # Get the file extension
            ext = format.split('/')[-1].split(';')[0]
            # Generate filename
            filename = f"{restaurant.subdirectory}_{dish.name}_{uuid.uuid4().hex[:6]}.{ext}"
            
            # Create ContentFile from base64 data
            image = ContentFile(base64.b64decode(imgstr), name=filename)
            dish.image = image

        dish.save()
        
        return JsonResponse({
            "message": "Dish updated successfully",
            "dish_id": dishid,
            "image_url": dish.image.url if dish.image else ""
        }, status=200)
        
    except Dish.DoesNotExist:
        return JsonResponse({"error": "Dish does not exist."}, status=404)
    except IntegrityError:
        return JsonResponse({
            "error": "A dish with this name already exists in your menu."
        }, status=400)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
@login_required
def delete_dish(request, dishid):
    try:
        dish = Dish.objects.get(id=dishid)
        
        # Add owner verification
        if request.user != dish.menu.subpage.kitchen.owner:
            return JsonResponse({"error": "Unauthorized"}, status=403)
            
        if request.method != "DELETE":  # Changed to DELETE method
            return JsonResponse({"error": "DELETE request required."}, status=400)
            
        dish.delete()
        return JsonResponse({
            "message": "Dish deleted successfully",
            "dish_id": dishid
        }, status=200)
        
    except Dish.DoesNotExist:
        return JsonResponse({"error": "Dish does not exist."}, status=404)

@csrf_exempt
@login_required
def delete_course(request, eatery, courseid):
    if request.method != "DELETE":
        return JsonResponse({"error": "DELETE request required."}, status=400)
    
    try:
        restaurant = get_object_or_404(Kitchen, subdirectory=eatery)
        
        # Check if user is owner
        if request.user != restaurant.owner:
            return JsonResponse({"error": "Unauthorized"}, status=403)

        course = get_object_or_404(Course, id=courseid)
        
        # Verify the course belongs to this restaurant's menu
        if course.menu.subpage.kitchen != restaurant:
            return JsonResponse({"error": "Course not found."}, status=404)

        # Delete the course (this will cascade delete all associated dishes)
        course.delete()

        return JsonResponse({
            "message": "Course and all associated dishes deleted successfully"
        }, status=200)

    except Exception as e:
        return JsonResponse({
            "error": str(e)
        }, status=400)


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

@login_required
def upload_image(request, model_name, object_id):
    if model_name not in ['kitchen', 'dish']:
        return HttpResponseBadRequest("Invalid model type")

    model = Kitchen if model_name == 'kitchen' else Dish
    obj = get_object_or_404(model, id=object_id)

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.uploaded_by = request.user
            image.content_type = ContentType.objects.get_for_model(obj)
            image.object_id = obj.id
            image.save()
            return redirect('object_detail', model_name=model_name, object_id=object_id)
    else:
        form = ImageUploadForm()

    return render(request, 'upload_image.html', {'form': form, 'object': obj})


def update_course_description(request, eatery, course_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    try:
        course = Course.objects.get(id=course_id)
        restaurant = get_object_or_404(Kitchen, subdirectory=eatery)
        
        # Verify owner
        if request.user != restaurant.owner:
            return JsonResponse({"error": "Unauthorized"}, status=403)
            
        data = json.loads(request.body)
        course.description = data.get('description', '').strip()
        course.save()
        
        return JsonResponse({
            "message": "Course description updated successfully",
            "course_id": course_id
        }, status=200)
        
    except Course.DoesNotExist:
        return JsonResponse({"error": "Course does not exist."}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    
def update_course_note(request, eatery, course_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    try:
        course = Course.objects.get(id=course_id)
        restaurant = get_object_or_404(Kitchen, subdirectory=eatery)
        
        # Verify owner
        if request.user != restaurant.owner:
            return JsonResponse({"error": "Unauthorized"}, status=403)
            
        data = json.loads(request.body)
        course.note = data.get('note', '').strip()
        course.save()
        
        return JsonResponse({
            "message": "Course note updated successfully",
            "course_id": course_id
        }, status=200)
        
    except Course.DoesNotExist:
        return JsonResponse({"error": "Course does not exist."}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    

@require_http_methods(["GET", "POST", "DELETE"])
def side_options(request, eatery, id):
    """
    Handles all side option operations:
    GET with course_id: Returns all side options for a course
    GET with side_id: Returns a specific side option
    POST with course_id: Creates a new side option
    POST with side_id: Updates an existing side option
    DELETE with side_id: Deletes a side option
    """
    try:
        restaurant = get_object_or_404(Kitchen, subdirectory=eatery)
        if request.user != restaurant.owner:
            return JsonResponse({"error": "Unauthorized"}, status=403)

        # GET request handling
        if request.method == "GET":
            try:
                # Try to get a specific side option
                side = SideOption.objects.get(id=id)
                return JsonResponse({
                    'id': side.id,
                    'name': side.name,
                    'description': side.description,
                    'price': str(side.price),
                    'is_premium': side.is_premium,
                    'course_id': side.course.id
                })
            except SideOption.DoesNotExist:
                # If not found, assume id is course_id and return all side options
                course = get_object_or_404(Course, id=id)
                side_options = course.side_options.all()
                return JsonResponse([{
                    'id': side.id,
                    'name': side.name,
                    'description': side.description,
                    'price': str(side.price),
                    'is_premium': side.is_premium
                } for side in side_options], safe=False)

        # POST request handling
        elif request.method == "POST":
            data = json.loads(request.body)
            
            try:
                # Try to get existing side option (update case)
                side = SideOption.objects.get(id=id)
                side.name = data.get('name', side.name)
                side.description = data.get('description', side.description)
                side.is_premium = data.get('is_premium', side.is_premium)
                side.price = data.get('price', side.price)
                side.save()
                course_id = side.course.id
            except SideOption.DoesNotExist:
                # If not found, create new side option
                course = get_object_or_404(Course, id=id)
                side = SideOption.objects.create(
                    course=course,
                    name=data.get('name'),
                    description=data.get('description', ''),
                    is_premium=data.get('is_premium', False),
                    price=data.get('price', 0)
                )
                course_id = course.id

            return JsonResponse({
                'message': 'Side option saved successfully',
                'course_id': course_id
            })

        # DELETE request handling
        elif request.method == "DELETE":
            side = get_object_or_404(SideOption, id=id)
            course_id = side.course.id
            side.delete()
            return JsonResponse({
                'message': 'Side option deleted successfully',
                'course_id': course_id
            })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@login_required
def preview_restaurant(request, eatery):
    try:
        restaurant = Kitchen.objects.get(subdirectory=eatery)
        
        # Check if user is the owner
        if request.user != restaurant.owner:
            return HttpResponseForbidden("You don't have permission to preview this restaurant")
            
        context = get_restaurant_context(restaurant, request.user, is_preview=True)
        return render(request, "visitor_layout.html", context)
        
    except Kitchen.DoesNotExist:
        return HttpResponseNotFound("Restaurant not found")


@login_required
def preview_menu(request, eatery):
    """Separate view for menu preview"""
    try:
        restaurant = Kitchen.objects.get(subdirectory=eatery)
        
        if request.user != restaurant.owner:
            return HttpResponseForbidden()
            
        # Get menu-specific data
        menus = Menu.objects.filter(kitchen=restaurant)
        courses = Course.objects.filter(menu__in=menus)
        dishes = Dish.objects.filter(course__in=courses)
        
        context = get_restaurant_context(restaurant, request.user, is_preview=True)
        context.update({
            'menus': menus,
            'courses': courses,
            'dishes': dishes,
        })
        
        return render(request, "kitchen_subpages/menu.html", context)
        
    except Kitchen.DoesNotExist:
        return HttpResponseNotFound()

@login_required
def preview_events(request, eatery):
    try:
        restaurant = Kitchen.objects.get(subdirectory=eatery)
        if request.user != restaurant.owner:
            return HttpResponseForbidden("You don't have permission to preview this restaurant")
            
        context = {
            'restaurant_details': restaurant,
            'events': Event.objects.filter(restaurant=restaurant),
            'is_preview': True
        }
        return render(request, 'restaurants/visitor_subpages/events.html', context)
    except Kitchen.DoesNotExist:
        return HttpResponseNotFound("Restaurant not found")
    
@login_required
def preview_about(request, eatery):
    try:
        restaurant = Kitchen.objects.get(subdirectory=eatery)
        if request.user != restaurant.owner:
            return HttpResponseForbidden("You don't have permission to preview this restaurant")
            
        context = {
            'restaurant_details': restaurant,
            'about': AboutUsPage.objects.filter(restaurant=restaurant),
            'is_preview': True
        }
        return render(request, 'restaurants/visitor_subpages/events.html', context)
    except Kitchen.DoesNotExist:
        return HttpResponseNotFound("Restaurant not found")


@login_required
def edit_layout(request, eatery):
    try:
        restaurant = get_object_or_404(Kitchen, subdirectory=eatery)
        if request.user != restaurant.owner:
            return HttpResponseForbidden()

        # Get or create subpages for each type
        subpages = {}
        current_page = request.GET.get('page', 'home')
        
        for page_type, label in SubPage.PAGE_TYPES:
            # Generate a unique slug for each page type
            slug = f"{restaurant.subdirectory}-{page_type}"
            
            subpage, created = SubPage.objects.get_or_create(
                kitchen=restaurant,
                page_type=page_type,
                defaults={
                    'title': f"{restaurant.restaurant_name} {label}",
                    'slug': slug,
                    'is_published': True
                }
            )
            subpages[page_type] = subpage

        # Get the current subpage for initial load
        current_subpage = subpages.get(current_page)

        context = {
            'restaurant_details': restaurant,
            'eatery': eatery,
            'subpages': subpages,  # Dictionary of all subpages
            'subpage': current_subpage,  # Current subpage for initial load
            'current_page': current_page,
            'hero_choices': SubPage.HERO_CHOICES,
            'nav_styles': Kitchen.NAV_CHOICES,
        }
        
        return render(request, "edit_layout.html", context)
        
    except Exception as e:
        logger.error(f"Error in edit_layout: {str(e)}")
        return HttpResponse(f"Error loading layout editor: {str(e)}", status=500)

@login_required
def preview_page(request, eatery, page_type):
    try:
        restaurant = get_object_or_404(Kitchen, subdirectory=eatery)
        if request.user != restaurant.owner:
            return HttpResponseForbidden()
            
        # For home page, we don't need a SubPage instance
        if page_type != 'home':
            subpage = get_object_or_404(SubPage, kitchen=restaurant, page_type=page_type)
        else:
            subpage = None
        
        # Get menu data if this is a menu page
        menu_data = None
        if page_type == 'menu':
            menus = Menu.objects.filter(kitchen=restaurant)
            menu_data = []
            for menu in menus:
                courses = Course.objects.filter(menu=menu).order_by('order')
                course_data = []
                for course in courses:
                    dishes = Dish.objects.filter(course=course).order_by('name')
                    course_data.append({
                        'name': course.name,
                        'description': course.description,
                        'dishes': dishes
                    })
                menu_data.append({
                    'name': menu.name,
                    'description': menu.description,
                    'courses': course_data
                })
        
        context = {
            'restaurant_details': restaurant,
            'subpage': subpage,
            'preview_mode': True,
            'eatery': eatery,
            'menu_data': menu_data,
            'is_home': page_type == 'home',
            'menu_page': page_type == 'menu',
            'about_page': page_type == 'about',
            'events_page': page_type == 'events',
        }
        
        # Map page types to their templates
        template_mapping = {
            'home': 'components/home/default.html',  # Use a default template for home
            'menu': f'components/menu/{restaurant.menu_style}.html',
            'about': 'components/about/default.html',
            'events': 'components/events/default.html',
        }
        
        template_name = template_mapping.get(page_type)
        if not template_name:
            raise ValueError(f"Invalid page type: {page_type}")
            
        logger.debug(f"Using template: {template_name}")
        return render(request, template_name, context)
        
    except Exception as e:
        logger.error(f"Error in preview_page: {str(e)}")
        return HttpResponse(f"Error loading preview: {str(e)}", status=500)
    
@login_required
def get_page_data(request, eatery, page_type):
    try:
        restaurant = get_object_or_404(Kitchen, subdirectory=eatery)
        if request.user != restaurant.owner:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
            
        subpage = get_object_or_404(SubPage, kitchen=restaurant, page_type=page_type)
        
        data = {
            'subpage_id': subpage.id,
            'hero_heading': subpage.hero_heading,
            'hero_subheading': subpage.hero_subheading,
            'hero_button_text': subpage.hero_button_text,
            'hero_layout': subpage.hero_layout,
            'hero_text_align': subpage.hero_text_align,
            'hero_text_color': subpage.hero_text_color,
            'hero_subtext_color': subpage.hero_subtext_color,
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        logger.error(f"Error in get_page_data: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
        
@login_required
def preview_component(request, eatery, component, style):
    try:
        restaurant = get_object_or_404(Kitchen, subdirectory=eatery)
        
        if request.user != restaurant.owner:
            return HttpResponseForbidden()
        
        template_name = None
        if component == 'navigation':
            template_name = f"components/navigation/top-nav/{style}.html"
        elif component == 'hero':
            template_name = f"components/hero/{style}.html"
        
        print(f"Looking for template: {template_name}")  # Debug log
        
        context = {
            'restaurant_details': restaurant,
            'eatery': eatery,
            'menu_page': True,
            'about_page': True,
            'events_page': True,
            'request': request,  # Add this for template context
        }
        
        try:
            html = render_to_string(template_name, context)
            return HttpResponse(html)
        except Exception as e:
            print(f"Template rendering error: {str(e)}")  # Debug log
            return HttpResponse(f"Error rendering template: {str(e)}", status=500)
            
    except Exception as e:
        print(f"View error: {str(e)}")  # Debug log
        return HttpResponse(f"Server error: {str(e)}", status=500)


@login_required
def preview_navigation(request, eatery, style):
    try:
        restaurant = get_object_or_404(Kitchen, subdirectory=eatery)
        if request.user != restaurant.owner:
            return HttpResponseForbidden()
        
        template_name = f"components/navigation/top-nav/{style}.html"
        context = {
            'restaurant_details': restaurant,
            'eatery': eatery,
            'menu_page': True,
            'about_page': True,
            'events_page': True,
        }
        
        html = render_to_string(template_name, context)
        return HttpResponse(html)
            
    except Exception as e:
        logger.error(f"Error in preview_navigation: {str(e)}")
        return HttpResponse(f"Error: {str(e)}", status=500)

@login_required
@require_POST
def update_global_component(request, eatery):
    try:
        restaurant = get_object_or_404(Kitchen, subdirectory=eatery)
        if request.user != restaurant.owner:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        data = json.loads(request.body)
        component = data.get('component')
        style = data.get('style')

        logger.debug(f"Updating component: {component} with style: {style}")

        # Map components to their model fields and choices
        component_map = {
            'navigation': ('navigation_style', Kitchen.NAV_CHOICES),
            'hero': ('hero_style', Kitchen.HERO_CHOICES),
        }

        if component not in component_map:
            return JsonResponse({'error': f'Invalid component: {component}'}, status=400)

        field_name, choices = component_map[component]
        valid_styles = [choice[0] for choice in choices]

        if style not in valid_styles:
            return JsonResponse({
                'error': f'Invalid {component} style. Got "{style}", expected one of: {valid_styles}'
            }, status=400)

        # Update only the specific field
        setattr(restaurant, field_name, style)
        
        # Save only the updated field
        restaurant.save(update_fields=[field_name])
        
        return JsonResponse({'success': True})

    except Exception as e:
        logger.error(f"Error in update_global_component: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
      
@require_POST
@login_required
def save_layout(request, eatery):
    """Save layout preferences"""
    restaurant = get_object_or_404(Kitchen, subdirectory=eatery, owner=request.user)
    
    try:
        data = json.loads(request.body)
        restaurant.navigation_style = data.get('navigation_style')
        restaurant.hero_style = data.get('hero_style')
        restaurant.primary_color = data.get('primary_color')
        restaurant.secondary_color = data.get('secondary_color')
        restaurant.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def upload_hero_image(request, eatery):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})

    try:
        restaurant = get_object_or_404(Kitchen, subdirectory=eatery)
        if request.user != restaurant.owner:
            return JsonResponse({'success': False, 'error': 'Unauthorized'})

        image_file = request.FILES.get('hero_image')
        if not image_file:
            return JsonResponse({'success': False, 'error': 'No image provided'})

        # Remove old hero image if it exists
        content_type = ContentType.objects.get_for_model(Kitchen)
        old_hero = Image.objects.filter(
            content_type=content_type,
            object_id=restaurant.id,
            alt_text__startswith='hero_'  # Use alt_text to identify hero images
        ).first()
        
        if old_hero:
            old_hero.delete()  # This will handle cleaning up the files

        # Create new hero image
        new_image = Image.objects.create(
            image=image_file,
            uploaded_by=request.user,
            content_type=content_type,
            object_id=restaurant.id,
            alt_text=f'hero_{restaurant.subdirectory}',  # Use this to identify hero images
            caption=f'Hero image for {restaurant.restaurant_name}'
        )

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def remove_hero_image(request, eatery):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})

    try:
        restaurant = get_object_or_404(Kitchen, subdirectory=eatery)
        if request.user != restaurant.owner:
            return JsonResponse({'success': False, 'error': 'Unauthorized'})

        content_type = ContentType.objects.get_for_model(Kitchen)
        hero_image = Image.objects.filter(
            content_type=content_type,
            object_id=restaurant.id,
            alt_text__startswith='hero_'
        ).first()

        if hero_image:
            hero_image.delete()

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def update_subpage_hero(request, eatery, subpage_id):
    try:
        restaurant = get_object_or_404(Kitchen, subdirectory=eatery)
        if request.user != restaurant.owner:
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

        subpage = get_object_or_404(SubPage, id=subpage_id, kitchen=restaurant)
        data = json.loads(request.body)
        
        field = data.get('field')
        value = data.get('value')

        valid_fields = ['heading', 'subheading', 'button_text', 'layout']
        if field not in valid_fields:
            return JsonResponse({'success': False, 'error': 'Invalid field'}, status=400)

        setattr(subpage, f'hero_{field}', value)
        subpage.save()

        return JsonResponse({'success': True})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
@login_required
@require_POST
def update_hero(request, eatery):
    try:
        restaurant = get_object_or_404(Kitchen, subdirectory=eatery)
        if request.user != restaurant.owner:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        data = json.loads(request.body)
        page_type = data.get('page_type')
        field = data.get('field')
        value = data.get('value')

        subpage = get_object_or_404(SubPage, kitchen=restaurant, page_type=page_type)
        
        valid_fields = [
            'heading', 'subheading', 'button_text', 'button_link',
            'layout', 'text_align', 'text_color', 'subtext_color'
        ]
        
        if field not in valid_fields:
            return JsonResponse({'error': 'Invalid field'}, status=400)

        setattr(subpage, f'hero_{field}', value)
        subpage.save()

        return JsonResponse({'success': True})

    except Exception as e:
        logger.error(f"Error in update_hero: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


