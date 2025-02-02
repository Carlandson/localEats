from allauth.account.forms import SignupForm
from allauth.account.views import SignupView
from django import forms
from django.contrib.auth import get_user_model
import uuid


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hide username field but don't remove it
        if 'username' in self.fields:
            self.fields['username'].widget = forms.HiddenInput()
            self.fields['username'].required = False

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email', '')
        
        # Generate username from email
        if email:
            base_username = email.split('@')[0][:30]
            username = base_username
            counter = 1
            User = get_user_model()
            
            # Keep trying until we get a unique username
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"[:30]
                counter += 1
                
            cleaned_data['username'] = username
        
        print("Form data:", cleaned_data)
        print("Form errors:", self.errors)
        return cleaned_data

    def save(self, request):
        try:
            user = super().save(request)
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
        print("POST data:", request.POST)
        return super().post(request, *args, **kwargs)

custom_signup = CustomSignupView.as_view()