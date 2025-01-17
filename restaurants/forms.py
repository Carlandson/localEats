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
from .models import Event
from django.utils.text import slugify
from .models import Image
from datetime import datetime, timedelta, date
from django.forms import ValidationError


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

class BusinessEditForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = [
            'business_name',
            'business_type',
            'description',
            'address',
            'phone_number',
            'email',
            'navigation_style',
            'footer_style',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'navigation_style': forms.RadioSelect(),
            'footer_style': forms.RadioSelect(),
        }

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
        
        # Get current datetime
        now = datetime.now()
        today = now.date()
        
        if start_date:
            # Check if start date is in the past
            if start_date < today:
                raise ValidationError("Event cannot be scheduled in the past")
            
            # If start date is today, check if time is in the past
            if start_date == today and start_time:
                start_datetime = datetime.combine(start_date, start_time)
                if start_datetime < now:
                    raise ValidationError("Event cannot be scheduled in the past")
        
        if start_date and start_time:
            cleaned_data['date'] = datetime.combine(start_date, start_time)
        
        if end_date and end_time:
            cleaned_data['end_date'] = datetime.combine(end_date, end_time)
            
            # Validate that end date is after start date
            if cleaned_data['end_date'] <= cleaned_data['date']:
                raise ValidationError("End date must be after start date")
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.date = self.cleaned_data['date']
        instance.end_date = self.cleaned_data.get('end_date')
        if commit:
            instance.save()
        return instance