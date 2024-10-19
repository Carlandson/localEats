from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class CustomAccountAdapter(DefaultAccountAdapter):
    def populate_username(self, request, user):
        """
        Generate a unique username for new users.
        """
        if not user.username:
            user.username = str(uuid.uuid4())[:30]
        return user

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        """
        Populate user information from social account.
        """
        user = super().populate_user(request, sociallogin, data)
        if not user.username:
            user.username = str(uuid.uuid4())[:30]
        return user