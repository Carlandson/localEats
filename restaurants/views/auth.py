def custom_logout(request):
    logout(request)
    return JsonResponse({'success': True})