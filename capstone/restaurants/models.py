from django.contrib.auth.models import AbstractUser
from django.db import models
from django_google_maps import fields as map_fields
from django_countries.fields import CountryField
from django.contrib.contenttypes.fields import GenericRelation

class User(AbstractUser):
    pass

class cuisine_categories(models.Model):
    cuisine = models.CharField(max_length=64)
    def __str__(self):
        return f"{self.cuisine}"

class menu_course(models.Model):
    course_list = models.CharField(max_length=64)
    def __str__(self):
        return f"{self.course_list}"

#https://github.com/SmileyChris/django-countries/
#https://pypi.org/project/django-google-maps/

class kitchen(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner")
    cuisine = models.ForeignKey(cuisine_categories, on_delete=models.CASCADE, related_name="cuisines")
    restaurant_name = models.CharField(max_length=64)
    address = map_fields.AddressField(max_length=200)
    geolocation = map_fields.GeoLocationField(max_length=200, blank=True)
    city = models.CharField(max_length=64)
    state = models.CharField(max_length=64)
    courses = models.ManyToManyField(menu_course, blank=True, related_name="kitchen_courses")
    country = CountryField()
    description = models.TextField(max_length=200, default="")
    created = models.DateTimeField(auto_now_add=True)
    user_favorite = models.ManyToManyField(User, blank=True, related_name="regular")
    phone_number = models.IntegerField(blank=True)
    def __str__(self):
        return f"{self.restaurant_name}"

    def regular_count(self):
        return self.user_favorite.count()

    def serialize(self):
        return {
            "cuisine": self.cuisine.cuisine,
            "name": self.restaurant_name,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "description": self.description
        }

class dish(models.Model):
    price = models.DecimalField(max_digits=6, decimal_places=2)
    name = models.CharField(max_length=64)
    recipe_owner = models.ForeignKey(kitchen, on_delete = models.CASCADE, related_name="kitchen")
    image_url = models.ImageField(upload_to='images')
    course = models.ForeignKey(menu_course, on_delete=models.CASCADE, related_name="courses")
    description = models.TextField(max_length=200, default="")
    date_added = models.DateField(auto_now=True)
    favorites = models.ManyToManyField(User, blank=True, related_name="user_favorite")

    def __str__(self):
        return f"{self.name}"

    def serialize(self):
        return {
            "name" : self.name,
            "price" : self.price,
            "kitchen": self.recipe_owner.restaurant_name,
            "course": self.course.course_list,
            "description": self.description,
            "image_url": self.image_url.url
        }

