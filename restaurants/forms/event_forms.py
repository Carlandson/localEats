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

class EventForm(forms.ModelForm):
    def get_min_date():
        """Returns today's date in YYYY-MM-DD format"""
        return date.today().strftime('%Y-%m-%d')
    # Start date/time fields
    start_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'min': get_min_date(),  # Set minimum date to today
                'class': "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 focus:ring-2 focus:ring-offset-2 transition-all duration-200",
                'onfocus': "this.classList.add('ring-2', 'ring-offset-2')",
                'onblur': "this.classList.remove('ring-2', 'ring-offset-2')"
            }
        ),
        label="Start Date"
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                'type': 'time',
                'class': "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 focus:ring-2 focus:ring-offset-2 transition-all duration-200",
                'onfocus': "this.classList.add('ring-2', 'ring-offset-2')",
                'onblur': "this.classList.remove('ring-2', 'ring-offset-2')"
            }
        ),
        label="Start Time"
    )
    
    # End date/time fields
    end_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'min': get_min_date(),  # Set minimum date to today
                'class': "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 focus:ring-2 focus:ring-offset-2 transition-all duration-200",
                'onfocus': "this.classList.add('ring-2', 'ring-offset-2')",
                'onblur': "this.classList.remove('ring-2', 'ring-offset-2')"
            }
        ),
        label="End Date"
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                'type': 'time',
                'class': "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 focus:ring-2 focus:ring-offset-2 transition-all duration-200",
                'onfocus': "this.classList.add('ring-2', 'ring-offset-2')",
                'onblur': "this.classList.remove('ring-2', 'ring-offset-2')"
            }
        ),
        label="End Time"
    )
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
                'accept': 'image/*',
                'class': "mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100",
            }
        ),
        label="Event Image"
    )

    class Meta:
        model = Event
        fields = ['title', 'description', 'image']

    def __init__(self, *args, **kwargs):
        self.business = kwargs.pop('business', None)
        instance = kwargs.get('instance', None)
        if instance:
            initial = kwargs.get('initial', {})
            initial['start_date'] = instance.date.date()
            initial['start_time'] = instance.date.time()
            if instance.end_date:
                initial['end_date'] = instance.end_date.date()
                initial['end_time'] = instance.end_date.time()
            kwargs['initial'] = initial
        
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'createEvent'
        self.helper.form_class = 'space-y-4'
        self.helper.form_method = 'POST'
        self.helper.form_enctype = 'multipart/form-data'
        
        self.helper.layout = Layout(
            Field('title', 
                css_class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 focus:ring-2 focus:ring-offset-2 transition-all duration-200",
                placeholder="Event Name"),
            
            HTML("<div class='space-y-4'>"),
            HTML("<h3 class='font-medium text-gray-700'>Event Start</h3>"),
            Div(
                Div(
                    Field('start_date', css_class="mt-1 block w-full"),
                    css_class="w-1/2 pr-2"
                ),
                Div(
                    Field('start_time', css_class="mt-1 block w-full"),
                    css_class="w-1/2 pl-2"
                ),
                css_class="flex -mx-2"
            ),
            
            HTML("<h3 class='font-medium text-gray-700 mt-4'>Event End</h3>"),
            Div(
                Div(
                    Field('end_date', css_class="mt-1 block w-full"),
                    css_class="w-1/2 pr-2"
                ),
                Div(
                    Field('end_time', css_class="mt-1 block w-full"),
                    css_class="w-1/2 pl-2"
                ),
                css_class="flex -mx-2"
            ),
            HTML("</div>"),
            
            Field('description',
                css_class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 focus:ring-2 focus:ring-offset-2 transition-all duration-200",
                rows="3",
                placeholder="Event Description"),
            
            Field('image',
                css_class="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100"),
            
            Div(
                HTML("""
                    <button type="button" class="cancel-add px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded transition-colors duration-200">
                        Cancel
                    </button>
                """),
                Submit('submit', 'Create Event', 
                    css_class='px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded transition-colors duration-200 ml-2'),
                css_class='flex justify-end space-x-2 mt-4'
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        start_time = cleaned_data.get('start_time')
        end_date = cleaned_data.get('end_date')
        end_time = cleaned_data.get('end_time')
        
        # Get current datetime in business timezone
        if self.business:
            tz = pytz.timezone(self.business.timezone)
            now = timezone.now().astimezone(tz)
        else:
            now = timezone.now()
        
        if start_date and start_time:
            # Create timezone-aware start datetime in business timezone
            start_datetime = datetime.combine(start_date, start_time)
            if self.business:
                start_datetime = tz.localize(start_datetime)
            else:
                start_datetime = timezone.make_aware(start_datetime)
            cleaned_data['date'] = start_datetime
            
            if start_datetime < now:
                raise ValidationError("Event cannot be scheduled in the past")
            
            if end_date and end_time:
                # Create timezone-aware end datetime in business timezone
                end_datetime = datetime.combine(end_date, end_time)
                if self.business:
                    end_datetime = tz.localize(end_datetime)
                else:
                    end_datetime = timezone.make_aware(end_datetime)
                cleaned_data['end_date'] = end_datetime
                
                if end_datetime <= start_datetime:
                    raise ValidationError("End date and time must be after start date and time")
        
        return cleaned_data

    def clean_end_date(self):
        """Individual field validation for end_date"""
        end_date = self.cleaned_data.get('end_date')
        logger.info(f"Cleaning end_date: {end_date}")
        return end_date

    def clean_end_time(self):
        """Individual field validation for end_time"""
        end_time = self.cleaned_data.get('end_time')
        logger.info(f"Cleaning end_time: {end_time}")
        return end_time

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.date = self.cleaned_data['date']
        instance.end_date = self.cleaned_data.get('end_date')
        if commit:
            instance.save()
        return instance
    