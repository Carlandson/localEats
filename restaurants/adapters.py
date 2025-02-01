from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.models import EmailAddress
from django.contrib import messages
from django.forms import ValidationError
import uuid

class CustomAccountAdapter(DefaultAccountAdapter):
    def clean_email(self, email):
        """
        Validates an email address. Raises ValidationError if the email is already taken.
        """
        email = super().clean_email(email)
        if EmailAddress.objects.filter(email__iexact=email).exists():
            raise ValidationError("This email address is already in use. Please sign in with your existing account.")
        return email

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        super().pre_social_login(request, sociallogin)
        
        email = sociallogin.account.extra_data.get('email')
        if email:
            try:
                existing_email = EmailAddress.objects.get(email__iexact=email)
                if existing_email:
                    if not sociallogin.is_existing:
                        sociallogin.connect(request, existing_email.user)
                        messages.info(request, "We've connected your Google account to your existing account.")
            except EmailAddress.DoesNotExist:
                pass

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        if not user.username:
            user.username = str(uuid.uuid4())[:30]
        return user