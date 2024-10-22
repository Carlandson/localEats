from allauth.account.forms import SignupForm
from allauth.account.views import SignupView
from django import forms
from django.core.exceptions import ValidationError
from .models import Kitchen, Dish
from django.forms import TextInput, ModelForm, Textarea
from django.core.mail import send_mail
from django.conf import settings

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

class RestaurantCreateForm(forms.ModelForm):
    class Meta:
        model = Kitchen
        fields = ['restaurant_name', 'phone_number', 'cuisine', 'address', 'city', 'state', 'country', 'description']
        widgets = {
            'restaurant_name': forms.TextInput(attrs={
                'class': 'mb-3',
                'style': 'max-width: 300px; border: solid 1px black;',
                'placeholder': 'name of restaurant',
            }),
            'phone_number': forms.TextInput(attrs={
                'style': 'border: solid 1px black;',
            }),
            'address': forms.Textarea(attrs={
                'class':'mb-3',
                'rows':'2',
                'style': 'border: solid 1px black; width: 300px;',
            }),
            'description': forms.Textarea(attrs={
                'class': 'mb-3',
                'style': 'border: solid 1px black; width: 200px;',
            }),
            'city': forms.TextInput(attrs={
                'style': 'border: solid 1px black;',
            }),
            'state': forms.TextInput(attrs={
                'style': 'border: solid 1px black;',
            }),
        }

    def save(self, commit=True):
        instance = super(RestaurantCreateForm, self).save(commit=False)
        instance.is_verified = False
        if commit:
            instance.save()
            self.send_verification_email(instance)
        return instance

    def send_verification_email(self, instance):
        subject = 'New Restaurant Submission'
        message = f"""
        A new restaurant has been submitted for verification:
        
        Name: {instance.restaurant_name}
        Phone: {instance.phone_number}
        Address: {instance.address}
        City: {instance.city}
        State: {instance.state}
        Country: {instance.country}
        Cuisine: {instance.cuisine}
        Description: {instance.description}
        
        Please verify this information and update the verification status in the admin panel.
        """
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [settings.ADMIN_EMAIL]  # Make sure to set this in your settings.py
        
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)

class DishSubmit(ModelForm):
    class Meta:
        model = Dish
        fields = ['name', 'course','price', 'image_url', 'description']