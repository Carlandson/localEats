from django.contrib import messages

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