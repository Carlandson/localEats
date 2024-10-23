from django.contrib.auth.models import AbstractUser
from django.db import models
from django_google_maps import fields as map_fields
from django_countries.fields import CountryField
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError


User = get_user_model()

class CuisineCategory(models.Model):
    cuisine = models.CharField(max_length=64)
    def __str__(self):
        return f"{self.cuisine}"
    
    def serialize(self):
        return {
            "id" : self.id,
            "cuisine" : self.cuisine
        }

class MenuCourse(models.Model):
    course_list = models.CharField(max_length=64)
    def __str__(self):
        return f"{self.course_list}"

#https://github.com/SmileyChris/django-countries/
#https://pypi.org/project/django-google-maps/

class Kitchen(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner")
    cuisine = models.ForeignKey(CuisineCategory, on_delete=models.CASCADE, related_name="cuisines")
    restaurant_name = models.CharField(max_length=64)
    address = map_fields.AddressField(max_length=200)
    geolocation = map_fields.GeoLocationField(max_length=200, blank=True)
    city = models.CharField(max_length=64)
    state = models.CharField(max_length=64)
    zip_code = models.CharField(max_length=20)
    courses = models.ManyToManyField(MenuCourse, blank=True, related_name="kitchen_courses")
    description = models.TextField(max_length=200, default="")
    created = models.DateTimeField(auto_now_add=True)
    user_favorite = models.ManyToManyField(User, blank=True, related_name="regular")
    phone_number = PhoneNumberField()
    is_verified = models.BooleanField(default=False)
    subdirectory = models.SlugField(max_length=64, unique=True)

    def clean(self):
        if Kitchen.objects.filter(subdirectory=self.subdirectory).exclude(pk=self.pk).exists():
            raise ValidationError({'subdirectory': 'This subdirectory is already in use. Please choose a different one.'})

    def save(self, *args, **kwargs):
        if not self.subdirectory:
            self.subdirectory = slugify(self.restaurant_name)
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.restaurant_name}"

    def regular_count(self):
        return self.user_favorite.count()
    
    @classmethod
    def verified_business_exists(cls, address):
        return cls.objects.filter(address=address, is_verified=True).exists()

    def clean(self):
        super().clean()
        if not self.pk and Kitchen.verified_business_exists(self.address):
            raise ValidationError("A verified business already exists at this address.")
        
    def serialize(self):
        return {
            "cuisine": self.cuisine.serialize(),
            "name": self.restaurant_name,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "description": self.description
        }

class Dish(models.Model):
    price = models.DecimalField(max_digits=6, decimal_places=2)
    name = models.CharField(max_length=64)
    recipe_owner = models.ForeignKey(Kitchen, on_delete = models.CASCADE, related_name="kitchen")
    image_url = models.ImageField(upload_to='images')
    course = models.ForeignKey(MenuCourse, on_delete=models.CASCADE, related_name="courses")
    description = models.TextField(max_length=200, default="")
    date_added = models.DateField(auto_now=True)
    favorites = models.ManyToManyField(User, blank=True, related_name="user_favorite")

    def __str__(self):
        return f"{self.name}"

    def serialize(self):
        return {
            "name" : self.name,
            "price" : str(self.price),
            "kitchen": self.recipe_owner.restaurant_name,
            "course": self.course.course_list,
            "description": self.description,
            "image_url": self.image_url.url if self.image_url else None
        }

