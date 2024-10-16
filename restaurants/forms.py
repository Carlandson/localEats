from allauth.account.forms import SignupForm
from django import forms
from django.core.exceptions import ValidationError

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