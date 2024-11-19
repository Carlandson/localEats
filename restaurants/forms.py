from allauth.account.forms import SignupForm
from allauth.account.views import SignupView
from django import forms
from .models import Business, Dish, CuisineCategory
from django.forms import ModelForm
from django.core.mail import send_mail
from django.conf import settings
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django.utils.text import slugify
from .models import Image

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
    phone_number = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(initial='US')
    )
    cuisine = forms.CharField(max_length=64) 
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
            'cuisine',
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