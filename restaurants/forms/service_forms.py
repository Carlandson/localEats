from allauth.account.forms import SignupForm
from allauth.account.views import SignupView
from django import forms
from ..models import Business, Dish, CuisineCategory
from django.forms import ModelForm
from django.core.mail import send_mail
from django.conf import settings
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div, HTML
from ..models import Event, HomePage, NewsFeed, NewsPost, Comment, AboutUsPage, ContactMessage, ContactPage, Product, ProductsPage, ServicesPage, Service
from django.utils.text import slugify
from ..models import Image
from datetime import datetime, timedelta, date
from django.forms import ValidationError
from django.utils import timezone
import pytz
import logging

logger = logging.getLogger(__name__)