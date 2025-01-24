from allauth.account.forms import SignupForm
from allauth.account.views import SignupView
from django import forms
from .models import Business, Dish, CuisineCategory
from django.forms import ModelForm
from django.core.mail import send_mail
from django.conf import settings
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div, HTML
from .models import Event, HomePage, NewsFeed, NewsPost, Comment, AboutUsPage
from django.utils.text import slugify
from .models import Image
from datetime import datetime, timedelta, date
from django.forms import ValidationError
from django.utils import timezone
import pytz
import logging

logger = logging.getLogger(__name__)


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')

    def clean(self):
        cleaned_data = super().clean()
        print("Form data:", cleaned_data)
        print("Form errors:", self.errors)  # Add this line
        return cleaned_data

    def save(self, request):
        try:
            user = super(CustomSignupForm, self).save(request)
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.save()
            print("User saved:", user)
            return user
        except Exception as e:
            print("Error saving user:", str(e))
            raise

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

class BusinessCreateForm(forms.ModelForm):
    phone_number = PhoneNumberField(region='US')
    cuisine = forms.CharField(max_length=64, required=False) 
    subdirectory = forms.SlugField(
        max_length=64, 
        required=False,
        label="Custom URL",
        widget=forms.TextInput(attrs={'placeholder': 'your-business-name'})
    )
    class Meta:
        model = Business
        fields = ['business_name', 'business_type', 'address', 'city', 'state', 'zip_code', 'phone_number', 'subdirectory', 'description']


    def clean_cuisine(self):
        cuisine_name = self.cleaned_data['cuisine']
        cuisine, created = CuisineCategory.objects.get_or_create(cuisine=cuisine_name)
        return cuisine
    
    def save(self, commit=True):
        instance = super(BusinessCreateForm, self).save(commit=False)
        instance.is_verified = False
        if commit:
            instance.save()
            self.send_verification_email(instance)
        return instance

    def clean_subdirectory(self):
        subdirectory = self.cleaned_data.get('subdirectory')
        if not subdirectory:
            subdirectory = slugify(self.cleaned_data.get('business_name'))
        
        if Business.objects.filter(subdirectory=subdirectory).exists():
            raise forms.ValidationError("This subdirectory is already in use. Please choose a different one.")
        
        return subdirectory
    
    def clean(self):
        cleaned_data = super().clean()
        address = cleaned_data.get('address')
        
        if address and Business.verified_business_exists(address):
            raise forms.ValidationError("A verified business already exists at this address.")
        
        return cleaned_data

    def send_verification_email(self, instance):
        subject = 'New Business Submission'
        message = f"""
        A new business has been submitted for verification:
        
        Name: {instance.business_name}
        Phone: {instance.phone_number}
        Address: {instance.address}
        City: {instance.city}
        State: {instance.state}
        Country: {instance.country}
        Business Type: {instance.business_type}
        Description: {instance.description}
        
        Please verify this information and update the verification status in the admin panel.
        """
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [settings.ADMIN_EMAIL]  # Make sure to set this in your settings.py
        
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['business_name'].widget.attrs.update({'placeholder': 'Name of business'})
        self.fields['description'].required = False  # Add this       

class DishSubmit(ModelForm):
    class Meta:
        model = Dish
        fields = ['name', 'description', 'price', 'image']  # Changed from image_url to image
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),  # Changed from URLInput to FileInput
        }

class BusinessEditForm(BusinessCreateForm):
    class Meta(BusinessCreateForm.Meta):
        fields = [
            'business_name',
            'business_type',
            'address',
            'city', 
            'state',
            'zip_code',
            'phone_number',
            'description',
            'cuisine',
            'email',
            'hours_of_operation',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'subdirectory' in self.fields:
            del self.fields['subdirectory']
        
        # Initialize Crispy Forms helper
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'space-y-6'
        
        # Create layout with sections
        self.helper.layout = Layout(
            # Basic Information Section
            HTML("<h3 class='text-lg font-medium text-gray-900 mb-4'>Basic Information</h3>"),
            Div(
                Field('business_name', css_class='mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500'),
                Field('business_type', css_class='mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500'),
                Field('description', css_class='mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500'),
                Field('cuisine', css_class='mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500'),
                css_class='space-y-4'
            ),
            
            # Contact Information Section
            HTML("<h3 class='text-lg font-medium text-gray-900 mt-6 mb-4'>Contact Information</h3>"),
            Div(
                Field('email', css_class='mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500'),
                Field('phone_number', css_class='mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500'),
                css_class='space-y-4'
            ),
            
            # Location Section
            HTML("<h3 class='text-lg font-medium text-gray-900 mt-6 mb-4'>Location</h3>"),
            Div(
                Field('address', css_class='mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500'),
                Div(
                    Div(
                        Field('city', css_class='mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500'),
                        css_class='col-span-2'
                    ),
                    Div(
                        Field('state', css_class='mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500'),
                        css_class='col-span-1'
                    ),
                    Div(
                        Field('zip_code', css_class='mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500'),
                        css_class='col-span-1'
                    ),
                    css_class='grid grid-cols-4 gap-4'
                ),
                css_class='space-y-4'
            ),
            
            # Hours Section
            HTML("<h3 class='text-lg font-medium text-gray-900 mt-6 mb-4'>Business Hours</h3>"),
            Field('hours_of_operation', css_class='mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500'),
            
            # Submit Button
            Div(
                Submit('submit', 'Save Changes', css_class='w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500'),
                css_class='mt-6'
            )
        )

    def save(self, commit=True):
        instance = super(BusinessCreateForm, self).save(commit=False)
        if commit:
            instance.save()
        return instance
    


class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image', 'alt_text', 'caption']


class BusinessCustomizationForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = [
            'navigation_style',
            'footer_style',
            'show_gallery',
            'show_testimonials',
            'show_social_feed',
            'show_hours',
            'show_map',
            'primary_color',
            'secondary_color',
            'hover_color',
            'text_color',
            'main_font',
        ]
        widgets = {
            'primary_color': forms.TextInput(attrs={'type': 'color'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color'}),
            'hover_color': forms.TextInput(attrs={'type': 'color'}),
            'text_color': forms.TextInput(attrs={'type': 'color'}),
            'main_font': forms.Select(attrs={'class': 'form-control'}),
            'hero_font': forms.Select(attrs={'class': 'form-control'}),
            'hero_heading_size': forms.Select(attrs={'class': 'form-control'}),
            'hero_subheading_size': forms.Select(attrs={'class': 'form-control'}),
            'body_font': forms.Select(attrs={'class': 'form-control'}),
            'body_size': forms.Select(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['navigation_style'].choices = Business.NAV_CHOICES
        self.fields['footer_style'].choices = Business.FOOTER_CHOICES


class BusinessImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image', 'alt_text', 'caption']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['alt_text'].help_text = "Use 'logo' for business logo or 'hero' for hero image"


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
    

# Home Page Form
class HomePageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        # Add Tailwind classes to form fields
        self.fields['welcome_title'].widget.attrs.update({
            'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
        })
        self.fields['welcome_message'].widget.attrs.update({
            'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            'rows': 4
        })
        
        self.helper.layout = Layout(
            Field('welcome_title', placeholder='Enter welcome title'),
            Field('welcome_message', placeholder='Enter welcome message'),
            Submit('submit', 'Save Changes', css_class='mt-4 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500')
        )

    class Meta:
        model = HomePage
        fields = [
            'welcome_title',
            'welcome_message',
            'show_welcome',
            'show_daily_special',
            'show_affiliates',
            'show_newsfeed',
            'show_upcoming_event',
            'show_featured_service',
            'show_featured_product'
        ]
        labels = {
            'show_welcome': 'Show Welcome Section',
            'show_daily_special': 'Show Daily Special',
            'show_affiliates': 'Show Affiliates',
            'show_newsfeed': 'Show News Feed',
            'show_upcoming_event': 'Show Upcoming Event',
            'show_featured_service': 'Show Featured Service',
            'show_featured_product': 'Show Featured Product'
        }

class NewsPostForm(forms.ModelForm):
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
                'accept': 'image/*',
                'class': "mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100",
            }
        ),
        label="Post Image"
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'  # Important for file uploads

        
        # Add Tailwind classes to form fields
        self.fields['title'].widget.attrs.update({
            'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            'placeholder': 'Enter news title'
        })
        self.fields['content'].widget.attrs.update({
            'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            'rows': 4,
            'placeholder': 'Enter news content'
        })
        
        self.helper.layout = Layout(
            Field('title', placeholder='Enter news title'),
            Field('content', placeholder='Enter news content'),
            Field('image',
                css_class="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"),
            Submit('submit', 'Post News', css_class='mt-4 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500')
        )

    class Meta:
        model = NewsPost
        fields = ['title', 'content', 'image']

class AboutUsForm(forms.ModelForm):
    # Main content fields
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full rounded-lg border-gray-300 focus:border-indigo-500 focus:ring-indigo-500',
            'rows': 4,
            'placeholder': 'Tell your story...'
        }),
        label="About Us Content",
        help_text="Share your business's main story and values"
    )
    
    history = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full rounded-lg border-gray-300 focus:border-indigo-500 focus:ring-indigo-500',
            'rows': 4,
            'placeholder': 'Share your history...'
        }),
        label="Our History",
        required=False,
        help_text="Tell the story of how your business started"
    )
    
    team_members = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full rounded-lg border-gray-300 focus:border-indigo-500 focus:ring-indigo-500',
            'rows': 4,
            'placeholder': 'Introduce your team...'
        }),
        label="Team Members",
        required=False,
        help_text="Introduce key team members"
    )

    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
                'accept': 'image/*',
                'class': "mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100",
            }
        ),
        label="Team Image",
        help_text="Upload an image of your team or business"
    )

    # Toggle fields for sections
    show_history = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500',
        }),
        label="Show History Section"
    )

    show_team = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500',
        }),
        label="Show Team Section"
    )

    # Mission and values (optional sections)
    mission_statement = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full rounded-lg border-gray-300 focus:border-indigo-500 focus:ring-indigo-500',
            'rows': 3,
            'placeholder': 'Our mission is...'
        }),
        required=False,
        label="Mission Statement",
        help_text="Share your business's mission"
    )

    core_values = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full rounded-lg border-gray-300 focus:border-indigo-500 focus:ring-indigo-500',
            'rows': 3,
            'placeholder': 'Our core values...'
        }),
        required=False,
        label="Core Values",
        help_text="List your business's core values"
    )

    show_mission = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500',
        }),
        label="Show Mission Statement"
    )

    show_values = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500',
        }),
        label="Show Core Values"
    )

    class Meta:
        model = AboutUsPage
        fields = [
            'content',
            'history',
            'team_members',
            'image',
            'show_history',
            'show_team',
            'mission_statement',
            'core_values',
            'show_mission',
            'show_values'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't render form tag, we'll handle it in template
        
        # Add any additional initialization if needed
        for field in self.fields.values():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({
                    'class': 'w-full rounded-lg border-gray-300 focus:border-indigo-500 focus:ring-indigo-500'
                })


