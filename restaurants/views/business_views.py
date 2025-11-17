# Django core imports
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.conf import settings

# Third-party imports
import googlemaps
import logging

# Local imports
from ..models import Business, SubPage
from ..forms import BusinessCreateForm
from .customize_views import get_editor_context
from .layout_views import get_visitor_context

logger = logging.getLogger(__name__)


@login_required
def create_business(request):
    user = request.user
    gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
    if request.method == "GET":
        context = {
            "create": BusinessCreateForm(),
            "owner": user,
            "google_maps_api_key": settings.GOOGLE_MAPS_API_KEY
        }
        return render(request, "create.html", context)

    if request.method == "POST":
        form = BusinessCreateForm(request.POST)
        if form.is_valid():
            new_business = form.save(commit=False)
            new_business.owner = user
            cuisine_data = request.POST.get('cuisine', '')
            if cuisine_data:
                cuisine_names = cuisine_data.split(',')
                cuisine_names = [name.strip() for name in cuisine_names if name.strip()]
            else:
                cuisine_names = None
            # Combine address components for geocoding
            full_address = f"{new_business.address}, {new_business.city}, {new_business.state} {new_business.zip_code}"

            try:
                # Geocode the address
                geocode_result = gmaps.geocode(full_address)

                if geocode_result:
                    location = geocode_result[0]['geometry']['location']
                    formatted_address = geocode_result[0]['formatted_address']
                    coordinates = f"{location['lat']},{location['lng']}"
                    timezone_result = gmaps.timezone(
                        location=(location['lat'], location['lng']),
                        timestamp=datetime.now().timestamp()
                    )
                    if timezone_result:
                        new_business.timezone = timezone_result['timeZoneId']
                    
                    if Business.verified_business_exists(formatted_address):
                        raise ValidationError("A verified business already exists at this address.")
                    
                    new_business.address = formatted_address

                    new_business.save()
                    # Create home page
                    home_page = SubPage.objects.create(
                        business=new_business,
                        page_type='home',
                        title=f"{new_business.business_name} Home",
                        is_published=True,
                        hero_heading=f"Welcome to {new_business.business_name}",
                        hero_subheading="We're excited to serve you!",
                        show_hero_heading=True,
                        show_hero_subheading=True
                    )
                    # Add cuisines to the menu if specified
                    if cuisine_names:
                        menu_page = SubPage.objects.create(
                            business=new_business,
                            page_type='menu',
                            title=f"{new_business.business_name} Menu",
                            is_published=True,
                            hero_heading="Our Menu",
                            hero_subheading="Explore our delicious offerings",
                            show_hero_heading=True,
                            show_hero_subheading=True
                        )

                        # Create menu and link it to the menu page
                        default_menu = Menu.objects.create(
                            business=new_business,
                            name=f"{new_business.business_name} Menu",
                            description="Our main menu",
                            subpage=menu_page,  # Link menu to the menu page
                            display_style='grid'
                        )
                        for cuisine_name in cuisine_names:
                            cuisine_category, created = CuisineCategory.objects.get_or_create(
                                cuisine=cuisine_name
                            )
                            default_menu.cuisine.add(cuisine_category)

                    messages.success(request, 'business created successfully!')
                    return redirect(reverse('business_home', kwargs={'business_subdirectory': new_business.subdirectory}))
                else:
                    messages.error(request, 'Unable to validate the address. Please check and try again.')
            except Exception as e:
                logger.error(f"Error creating Business: {str(e)}", exc_info=True)
                messages.error(request, f'An error occurred: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
            logger.error(f"Form validation errors: {form.errors}")

        context = {
            "create": form,
            "google_maps_api_key": settings.GOOGLE_MAPS_API_KEY
        }
        return render(request, "create.html", context)


def get_business_context(business, user, page_type='home'):
    """Base context for both editor and visitor views"""
    is_dashboard = page_type == 'dashboard'
    is_owner = user == business.owner
    
    # Get the requested subpage
    subpage = SubPage.objects.filter(
        business=business, 
        page_type=page_type if not is_dashboard else 'home'
    ).first()
    print(subpage)
    # Base context needed for both views
    base_context = {
        'business_details': business,
        'business_subdirectory': business.subdirectory,
        'subpage': subpage,
        'is_owner': is_owner,
        'is_edit_page': is_owner and not is_dashboard,
    }

    if is_owner:
        return get_editor_context(base_context, business, subpage, page_type)
    else:
        return get_visitor_context(base_context, business, subpage, page_type)
    

def business_dashboard(request, business_subdirectory):
    business = get_object_or_404(Business, subdirectory=business_subdirectory)
    
    # Check if user is the business owner
    if request.user != business.owner:
        return redirect('business_home', business_subdirectory=business_subdirectory)
    
    if request.method != "GET":
        return JsonResponse({"error": "GET request required."}, status=400)

    # Get context for the dashboard
    context = get_business_context(business, request.user, 'dashboard')
    
    return render(request, "eatery_owner.html", context)

def business_subpage_editor(request, business_subdirectory, page_type):
    business = get_object_or_404(Business, subdirectory=business_subdirectory)
    context = get_business_context(business, request.user, page_type)
    return render(request, "subpages/events.html", context)


def business_page(request, business_subdirectory, page_type="home"):
    business = get_object_or_404(Business, subdirectory=business_subdirectory)
    
    if request.method != "GET":
        return JsonResponse({"error": "GET request required."}, status=400)

    # Get context with specified page type
    context = get_business_context(business, request.user, page_type)
    # Check verification status
    if not business.is_verified and request.user != business.owner:
        return render(request, "business_under_construction.html", context)

    # Determine which template to use
    if request.user == business.owner:
        template = f"subpages/{page_type}.html" 
    else:
        template = f"visitor_pages/{page_type}.html"

    return render(request, template, context)


def business_main(request, business_subdirectory):
    business = get_object_or_404(Business, subdirectory=business_subdirectory)
    
    if request.method != "GET":
        return JsonResponse({"error": "GET request required."}, status=400)

    # Get or create home subpage
    subpage, created = SubPage.objects.get_or_create(
        business=business,
        page_type='home',
        defaults={
            'title': business.business_name,
            'slug': business.subdirectory,
            'is_published': True
        }
    )
    # Get your existing context
    context = get_business_context(business, request.user)
    
    # Add subpage to context
    context.update({
        'subpage': subpage,
        'is_home': True
    })
    print(business.is_verified)

    if not business.is_verified and request.user != business.owner:
        return render(request, "business_under_construction.html", context)

    if request.user == business.owner:
        return render(request, "eatery_owner.html", context)
    else:
        return render(request, "visitor_pages/home.html", context)
    

def get_business(request, business_id):
    try:
        business_obj = Business.objects.get(id=business_id)
        return JsonResponse(business_obj.serialize())
    except Business.DoesNotExist:
        return JsonResponse({"error": "Business not found"}, status=404)