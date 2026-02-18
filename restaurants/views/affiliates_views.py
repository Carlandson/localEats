from django.shortcuts import render, get_object_or_404
from ..models import Business

def affiliates_dashboard(request, business_subdirectory):
    business = get_object_or_404(Business, subdirectory=business_subdirectory)
    return render(request, 'affiliates/dashboard.html', {'business': business})