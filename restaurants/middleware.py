from django.contrib import messages
import base64
from django.http import HttpResponse
from django.conf import settings

class ClearMessagesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Clear messages at the beginning of each request
        storage = messages.get_messages(request)
        storage.used = True

        response = self.get_response(request)
        return response
    
class JavaScriptMimeTypeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.endswith('.js'):
            response['Content-Type'] = 'application/javascript'
        return response
    
class BasicAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not settings.DEBUG:
            if 'HTTP_AUTHORIZATION' not in request.META:
                return self.unauthorized_response()
            
            auth = request.META['HTTP_AUTHORIZATION'].split()
            if len(auth) != 2 or auth[0].lower() != 'basic':
                return self.unauthorized_response()
            
            username, password = base64.b64decode(auth[1]).decode().split(':')
            if username != settings.BASIC_AUTH_USERNAME or password != settings.BASIC_AUTH_PASSWORD:
                return self.unauthorized_response()
        
        return self.get_response(request)

    def unauthorized_response(self):
        response = HttpResponse('Unauthorized', status=401)
        response['WWW-Authenticate'] = 'Basic realm="Restricted Access"'
        return response