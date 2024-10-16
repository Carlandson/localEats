import json
import geopy.distance

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.forms import TextInput, ModelForm, Textarea
from geopy.geocoders import Nominatim
from .models import User, Kitchen, MenuCourse, Dish, CuisineCategory
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

User = get_user_model()

class restaurant_create(ModelForm):
    class Meta:
        model = Kitchen
        fields = ['restaurant_name', 'phone_number', 'cuisine', 'address', 'city', 'state', 'country', 'description']
        widgets = {
            'restaurant_name': TextInput(attrs={
                'class': 'mb-3',
                'style': 'max-width: 300px;',
                'placeholder': 'name of restaurant',
                'style': 'border: solid 1px black',
            }),
            'phone_number': TextInput(attrs={
                'style': 'border: solid 1px black',
            }),
            'address': Textarea(attrs={
                'class':'mb-3',
                'rows':'2',
                'style': 'border: solid 1px black; width: 300px',
            }),
            'description': Textarea(attrs={
                'class': 'mb-3',
                'style': 'border: solid 1px black; width: 200px',
            }),
            'city': TextInput(attrs={
                'style': 'border: solid 1px black',
            }),
            'state': TextInput(attrs={
                'style': 'border: solid 1px black',
            }),
        }

class dish_submit(ModelForm):
    class Meta:
        model = Dish
        fields = ['name', 'course','price', 'image_url', 'description']

class CustomSignupView(SignupView):
    form_class = CustomSignupForm

    def form_invalid(self, form):
        print("Form is invalid")
        print("Form errors:", form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        print("Form is valid")
        response = super().form_valid(form)
        print("Response:", response)
        return response
    
    def post(self, request, *args, **kwargs):
        print("POST data:", request.POST)  # Debug print
        return super().post(request, *args, **kwargs)

custom_signup = CustomSignupView.as_view()
# def index(request):
#     if request.user.is_authenticated:
#         if request.method != "GET":
#             return JsonResponse({"error" : "GET request required."}, status=400)
#         collection = []
#         kitchen_list = kitchen.objects.all().order_by('-created')
#         return render(request, "restaurant/index.html", {"recently_rated": collection, "kitchen_list": kitchen_list})
#     else:
#         return HttpResponseRedirect(reverse("login"))

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

# def login_view(request):
#     if request.method == "POST":
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             user = form.user
#             remember_me = form.cleaned_data.get('remember', False)
#             if user is not None:
#                 perform_login(request, user, remember=remember_me)
#                 messages.success(request, "Successfully logged in.")
#                 return redirect('/')
#         else:
#             messages.error(request, "Invalid username and/or password.")
#     else:
#         form = LoginForm()
    
#     return render(request, "account/login.html", {'form': form})

# def logout_view(request):
#     auth_logout(request)
#     messages.success(request, "You have been logged out.")
#     return redirect(reverse("index"))

# @transaction.atomic
# def register(request):
#     if request.method == "POST":
#         username = request.POST["username"]
#         email = request.POST["email"]
#         password = request.POST["password"]
#         confirmation = request.POST["confirmation"]
#         if password != confirmation:
#             return render(request, "account/signup.html", {
#                 "message": "Passwords must match."
#             })
#         try:
#             with transaction.atomic():
#                 user = User.objects.create_user(username, email, password)
#                 user.save()
                
#                 # Create EmailAddress instance for allauth
#                 EmailAddress.objects.create(user=user, email=email, primary=True, verified=False)
                
#                 # Use allauth's perform_login
#                 perform_login(request, user, email_verification='optional')
            
#             # Use reverse() to generate the URL, then pass it to redirect()
#             return redirect(reverse('my_profile'))
#         except IntegrityError:
#             return render(request, "account/signup.html", {
#                 "message": "Username or email already taken."
#             })
#     else:
#         return render(request, "account/signup.html")

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
    usern = request.user
    geolocator = Nominatim(user_agent="restaurants")
    if request.method == "GET":
        return render(request, "create.html", {"owner": usern, "create": restaurant_create()})
    if request.method == "POST":
        form = restaurant_create(request.POST)
        if form.is_valid():
            restaurant_name = form.cleaned_data['restaurant_name']
            address = form.cleaned_data['address']
            description = form.cleaned_data['description']
            state = form.cleaned_data['state']
            cuisine = form.cleaned_data['cuisine']
            country = form.cleaned_data['country']
            city = form.cleaned_data['city']
            phone_number = form.cleaned_data['phone_number']
        else:
            print(form.errors)
            return render(request, "create.html", {"create" : restaurant_create()})
        location = geolocator.geocode(address + " " + city)
        coordinates = f"{location.latitude},{location.longitude}"
        new_restaurant = Kitchen(owner=usern, phone_number=phone_number, city=city, restaurant_name=restaurant_name, address=address, description=description, state=state, country=country, cuisine=cuisine, geolocation=coordinates)
        new_restaurant.save()
        return redirect(reverse('eatery', kwargs={'eatery': new_restaurant.restaurant_name}))
        # return HttpResponseRedirect(reverse('eatery', kwargs={'eatery' : new_restaurant.restaurant_name}))

def eatery(request, eatery):
    course_list = MenuCourse.objects.all()
    restaurant_get = Kitchen.objects.get(restaurant_name=eatery)
    dishes = Dish.objects.filter(recipe_owner=restaurant_get)
    courses = restaurant_get.courses.all()
    #rating = Rating.objects.all().order_by("-average")
    #top_ratings = []
    #for item in rating:
        #if item.average > 3:
            #for i in dishes:
                #if item.object_id == i.id:
                    #top_ratings.append(i)
    if restaurant_get.owner == request.user:
        owner = True
        if request.method == "GET":
            return render(request, "eatery.html", {"eatery": eatery, "restaurant_details": restaurant_get, "owner":owner, "courses":courses, "dishes":dishes, "course_list":course_list})
    else:
        owner = False
        if request.method != "GET":
            return JsonResponse({"error" : "GET request required."}, status=400)
        if request.method == "GET":
            return render(request, "eatery.html", {"eatery": eatery, "restaurant_details": restaurant_get, "owner":owner, "courses":courses, "dishes":dishes, "course_list":course_list})

@login_required
def new_dish(request, kitchen_name):
    if request.method == "GET":
        return render(request, "newdish.html", {"new_dish" : dish_submit()})
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
            return render(request, "newdish.html", {"new_dish" : dish_submit()})
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