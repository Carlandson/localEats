from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.models import EmailAddress
from django.contrib import messages
from django.forms import ValidationError
import uuid
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

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
        try:
            # Call parent's pre_social_login first
            super().pre_social_login(request, sociallogin)
            
            # Get email from social account
            email = sociallogin.account.extra_data.get('email')
            if email:
                try:
                    # Check if email exists
                    existing_email = EmailAddress.objects.get(email__iexact=email)
                    if existing_email:
                        if not sociallogin.is_existing:
                            # Connect social account to existing user
                            sociallogin.connect(request, existing_email.user)
                            messages.info(request, "Connected your Google account to your existing account.")
                except EmailAddress.DoesNotExist:
                    pass
        except Exception as e:
            logger.error(f"Social login error: {str(e)}")
            messages.error(request, "There was an error with the social login. Please try again.")
            raise

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        try:
            # Set email
            user.email = data.get('email', '')
            
            # Set name fields if available
            name_data = data.get('name', '').split(' ', 1)
            if len(name_data) > 0:
                user.first_name = name_data[0]
            if len(name_data) > 1:
                user.last_name = name_data[1]
                
        except Exception as e:
            logger.error(f"Error populating user: {str(e)}")
        return user