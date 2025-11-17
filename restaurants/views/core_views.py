import logging

# Django core imports
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.conf import settings

# Third-party imports
import googlemaps
from datetime import datetime

# Local imports
from ..models import Business, SubPage
from ..forms import BusinessCreateForm, BusinessEditForm

logger = logging.getLogger(__name__)

def index(request): 
    business_list = Business.objects.all().order_by('-created')
    paginator = Paginator(business_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = {
            'businesses': [
                {
                    'name': business.business_name,
                    'business_type': business.business_type,
                    'city': business.city,
                    'state': business.state,
                    'cuisines': list(business.menus.first().cuisine.values_list('cuisine', flat=True)) if business.menus.exists() else [],
                    'created': business.created.strftime('%B %d, %Y'),
                    'url': reverse('business_home', args=[business.subdirectory])
                } for business in page_obj
            ],
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'num_pages': paginator.num_pages,
            'current_page': page_obj.number
        }
        return JsonResponse(data)

    return render(request, 'index.html', {'page_obj': page_obj})

def profile(request):
    business_list = Business.objects.all()
    owner_business = []
    owner_check = False
    print(business_list)
    for business in business_list:
        if business.owner == request.user:
            owner_business.append(business)
            owner_check = True
    return render(request, "profile.html", {"profile": profile, "owner_check" : owner_check, "owner_business" : owner_business})


def aboutus(request):
    return render(request, "aboutus.html")

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
    
@login_required
def edit_business(request, business_subdirectory):
    business = get_object_or_404(Business, subdirectory=business_subdirectory, owner=request.user)
    
    if request.method == 'POST':
        print(request.POST)
        form = BusinessEditForm(request.POST, instance=request.user.business)
        if form.is_valid():
            business = form.save()
            # Return only the updated field value
            field_name = next(iter(form.changed_data))  # Get the first (and should be only) changed field
            return JsonResponse({
                field_name: getattr(business, field_name)
            })
        return JsonResponse({'error': 'Invalid form data'}, status=400)
    else:
        form = BusinessEditForm(instance=business)
    
    return render(request, 'subpages/edit_business.html', {
        'form': form,
        'instance': business,
        'business_details': business,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
        'is_edit_page': True,
        'is_owner': True,
    })

@login_required
def update_business_field(request, business_subdirectory):
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    business = get_object_or_404(Business, subdirectory=business_subdirectory)
    
    # Get the field being updated from the request
    field_name = request.POST.get('field_name')
    if not field_name:
        return JsonResponse({'error': 'No field specified'}, status=400)
    
    # Get the new value
    new_value = request.POST.get(field_name)
    current_value = str(getattr(business, field_name))

    # If the value hasn't changed, return success without doing anything
    if new_value == current_value:
        return JsonResponse({
            'status': 'success',
            field_name: current_value
        })
    
    # Create a form with only the specific field data
    form_data = {field_name: new_value}
    form = BusinessEditForm(form_data, instance=business)
    
    # Validate only the specific field
    form.fields = {field_name: form.fields[field_name]}
    
    if form.is_valid():
        try:
            # If updating address, check for existing verified business
            if field_name == 'address':
                new_address = form.cleaned_data[field_name]
                existing_business = Business.objects.filter(
                    address=new_address,
                    is_verified=True
                ).exclude(id=business.id).first()
                
                if existing_business:
                    return JsonResponse({
                        'status': 'error',
                        'errors': ['A verified business already exists at this address. Please contact support if this is your business.']
                    }, status=400)
            
            # Update the field if validation passes
            setattr(business, field_name, form.cleaned_data[field_name])
            business.save(update_fields=[field_name])
            
            return JsonResponse({
                'status': 'success',
                field_name: str(getattr(business, field_name))
            })
            
        except ValidationError as e:
            return JsonResponse({
                'status': 'error',
                'errors': [str(e)]
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'errors': ['An unexpected error occurred. Please try again.']
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'errors': form.errors.get(field_name, ['Invalid data'])
    }, status=400)