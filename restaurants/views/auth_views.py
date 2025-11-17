
# Django core imports
from django.contrib.auth import logout
from django.contrib.auth import get_user_model
from django.http import JsonResponse

# Local imports
from ..forms import CustomSignupView

User = get_user_model()

custom_signup = CustomSignupView.as_view()


def custom_logout(request):
    logout(request)
    return JsonResponse({'success': True})