from django.contrib.auth.models import AbstractUser
from django.db import models
from django_google_maps import fields as map_fields
from django_countries.fields import CountryField
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.auth import get_user_model
from django.utils.text import slugify


User = get_user_model()

class CustomUser(AbstractUser):
    username = None  # Remove username field
    email = models.EmailField('email address', unique=True)
    display_name = models.CharField(max_length=50, blank=True)
    slug = models.SlugField(unique=True, blank=True)

    # Add custom related_name arguments
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='customuser_set',
        related_query_name='customuser',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_set',
        related_query_name='customuser',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def get_display_name(self):
        return self.display_name or f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = f"{self.first_name} {self.last_name}"
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        base_slug = slugify(self.get_display_name())
        unique_slug = base_slug
        num = 1
        while CustomUser.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{base_slug}-{num}"
            num += 1
        return unique_slug

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
    courses = models.ManyToManyField(MenuCourse, blank=True, related_name="kitchen_courses")
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

