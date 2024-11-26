from django.conf import settings

def user_data(request):
    user = request.user
    if user.is_authenticated:
        return {
            'user_display_name': user.get_full_name() or user.username,
            'user_email': user.email,
            'user_id': user.id,
        }
    return {}


def debug_settings(request):
    return {
        'debug': settings.DEBUG
    }