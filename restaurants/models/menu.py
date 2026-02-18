from django.db import models
from django.contrib.auth import get_user_model
import logging

from .content import SubPage
from .business import Business


logger = logging.getLogger(__name__)
# Image, SubPage, Menu, Course, Dish, AboutUsPage, EventsPage, Event, SpecialsPage, business, CuisineCategory
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
    
class Menu(models.Model):

    MENU_DISPLAY_CHOICES = [
        ('grid', 'Grid Layout'),
        ('list', 'List Layout'),
        ('cards', 'Card Layout'),
    ]
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="menus")
    cuisine = models.ManyToManyField(CuisineCategory, related_name="menu_cuisines", blank=True)
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    subpage = models.ForeignKey(SubPage, on_delete=models.SET_NULL, null=True, related_name='menu_content')
    display_style = models.CharField(max_length=20, choices=MENU_DISPLAY_CHOICES, default='grid')

    def __str__(self):
        return f"{self.business.business_name} - {self.name}"

class Course(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="courses")
    name = models.CharField(max_length=64)
    order = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    note = models.TextField(blank=True, null=True)  

    class Meta:
        ordering = ['order']

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)


    def __str__(self):
        return f"{self.menu.name} - {self.name}"

    def serialize(self):
        return {
            "name": self.name,
            "menu": self.menu.name
        }

class Dish(models.Model):
    price = models.DecimalField(max_digits=6, decimal_places=2)
    name = models.CharField(max_length=64)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="dishes")
    image = models.ImageField(upload_to='dishes/', null=True, blank=True) 
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="dishes")
    description = models.TextField(max_length=200, default="")
    date_added = models.DateField(auto_now=True)
    favorites = models.ManyToManyField(User, blank=True, related_name="user_favorite")
    is_special = models.BooleanField(default=False)
    special_price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    included_sides = models.IntegerField(default=0)
    # new fields
    happy_hour = models.BooleanField(default=False)
    happy_hour_price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ['course', 'name']
    def __str__(self):
        return f"{self.name}"

    def serialize(self):
        return {
            "name" : self.name,
            "price" : str(self.price),
            "business": self.menu.business,
            "course": self.course.course_list,
            "description": self.description,
            "image_url": self.image_url.url if self.image_url else None
        }

class SideOption(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='side_options')
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    is_premium = models.BooleanField(default=False)
    available = models.BooleanField(default=True)

class SpecialsPage(models.Model):
    subpage = models.OneToOneField(SubPage, on_delete=models.CASCADE, related_name='specials_content')
    happy_hour_start = models.TimeField(null=True, blank=True)
    happy_hour_end = models.TimeField(null=True, blank=True)
    happy_hour_days = models.CharField(max_length=100, blank=True, help_text="Comma-separated days, e.g., 'Mon,Tue,Wed'")

class DailySpecial(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    specials_page = models.ForeignKey(SpecialsPage, on_delete=models.CASCADE, related_name='daily_specials')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    dishes = models.ManyToManyField('Dish', limit_choices_to={'is_special': True})
    is_active = models.BooleanField(default=True)