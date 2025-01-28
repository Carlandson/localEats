from django import forms
from ..models import Business, CuisineCategory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div, HTML
from phonenumber_field.formfields import PhoneNumberField
from django.utils.text import slugify
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

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

class BusinessEditForm(BusinessCreateForm):
    class Meta(BusinessCreateForm.Meta):
        fields = [
            'business_name',
            'business_type',
            'address',
            'phone_number',
            'description',
            'cuisine',
            'email',
            'hours_of_operation',
            'geolocation',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'space-y-6'
        self.fields['address'].widget.attrs.update({
            'id': 'address-input',
            'class': 'address-autocomplete',
            'data-geo-id': 'id_geolocation'  # Link to hidden geolocation field
        })
        
        self.helper.layout = Layout(
            # Basic Information Section
            HTML("<h3 class='text-lg font-medium text-gray-900 mb-4'>Basic Information</h3>"),
            *[self.create_editable_field(field) for field in [
                'business_name', 'business_type', 'description'
            ]],
            
            # Contact Information Section
            HTML("<h3 class='text-lg font-medium text-gray-900 mt-6 mb-4'>Contact Information</h3>"),
            *[self.create_editable_field(field) for field in [
                'email', 'phone_number'
            ]],
            
            # Location Section
            HTML("<h3 class='text-lg font-medium text-gray-900 mt-6 mb-4'>Location</h3>"),
            self.create_address_field(),  # Special handling for address
            
            # Hours Section
            HTML("<h3 class='text-lg font-medium text-gray-900 mt-6 mb-4'>Business Hours</h3>"),
            self.create_editable_field('hours_of_operation'),
        )
    def create_address_field(self):
        """Special handling for address field with Google Maps integration"""
        return Div(
            Div(
                HTML("""
                    <div class="field-display-wrapper">
                        <div data-field="address" class="flex justify-between items-center p-4 bg-white rounded-lg border border-gray-200">
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Address</label>
                                <div class="mt-1 text-gray-900">{{ instance.address }}</div>
                            </div>
                            <button type="button" 
                                    class="edit-button ml-4 inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500">
                                Change Address
                            </button>
                        </div>
                    </div>
                """),
                Div(
                    HTML("""
                        <div class="mb-4">
                            <div id="map" class="h-64 w-full rounded-lg mb-4"></div>
                        </div>
                    """),
                    Field('address', css_class="address-autocomplete mb-4"),
                    Field('geolocation', type="hidden"),
                    Div(
                        HTML("""
                            <button type="button" class="save-button mr-2 inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500">
                                Save
                            </button>
                            <button type="button" class="cancel-button inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500">
                                Cancel
                            </button>
                        """),
                        css_class='mt-3 flex justify-end'
                    ),
                    css_class='field-edit-wrapper hidden p-4 bg-gray-50 rounded-lg border border-gray-200 mt-2'
                ),
                css_class='mb-4'
            )
        )
    def create_editable_field(self, field_name):
        # Special handling for address field to show street address
        display_value = "{{ instance.street_address }}" if field_name == 'address' else "{{ instance." + field_name + " }}"
        
        return Div(
            Div(
                HTML(f"""
                    <div class="field-display-wrapper">
                        <div data-field="{field_name}" class="flex justify-between items-center p-4 bg-white rounded-lg border border-gray-200">
                            <div>
                                <label class="block text-sm font-medium text-gray-700">{self.fields[field_name].label}</label>
                                <div class="mt-1 text-gray-900">{display_value}</div>
                            </div>
                            <button type="button" 
                                    class="edit-button ml-4 inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500">
                                Edit
                            </button>
                        </div>
                    </div>
                """),
                Div(
                    Field(field_name),
                    Div(
                        HTML("""
                            <button type="button" class="save-button mr-2 inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500">
                                Save
                            </button>
                            <button type="button" class="cancel-button inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500">
                                Cancel
                            </button>
                        """),
                        css_class='mt-3 flex justify-end'
                    ),
                    css_class='field-edit-wrapper hidden p-4 bg-gray-50 rounded-lg border border-gray-200 mt-2'
                ),
                css_class='mb-4'
            )
        )
    

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
    