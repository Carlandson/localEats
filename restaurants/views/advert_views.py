from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def seo(request, business_subdirectory):
    return render(request, 'subpages/seo.html')

@login_required
def advertising(request, business_subdirectory):
    return render(request, 'subpages/advertising.html')