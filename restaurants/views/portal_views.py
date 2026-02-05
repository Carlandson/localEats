from django.shortcuts import render

def portal(request, business_subdirectory):
    return render(request, "subpages/portal.html")