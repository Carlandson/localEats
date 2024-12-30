import json
import geopy.distance
import logging
from PIL import Image as PILImage
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound, HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.core.paginator import Paginator
from .models import Image, SubPage, Menu, Course, Dish, AboutUsPage, EventsPage, Event, SpecialsPage, Business, CuisineCategory, SideOption
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from google.auth.exceptions import RefreshError
from googleapiclient.errors import HttpError
from django.views.decorators.csrf import ensure_csrf_cookie
from googleapiclient.discovery import build
import google_auth_httplib2
import httplib2
from allauth.socialaccount.models import SocialAccount
from google.oauth2.credentials import Credentials
from django.core.mail import send_mail
from django.conf import settings
from .forms import BusinessCreateForm, DishSubmit, CustomSignupView, ImageUploadForm, BusinessCustomizationForm
from django.contrib.contenttypes.models import ContentType
from django.db.models import Max
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.utils import timezone
from .constants import get_font_choices, get_font_sizes
import base64, uuid
import googlemaps

User = get_user_model()

custom_signup = CustomSignupView.as_view()

def some_view(request):
       send_mail(
           'Test Subject',
           'Test message.',
           settings.DEFAULT_FROM_EMAIL,
           ['to@example.com'],
           fail_silently=False,
       )



logger = logging.getLogger(__name__)

@login_required
def fetch_business_info(request):
    try:
        social_account = SocialAccount.objects.get(user=request.user, provider='google')
        social_token = social_account.socialtoken_set.first()
        
        if not social_token:
            logger.warning("No Google token found for user %s", request.user.username)
            messages.error(request, 'No Google token found. Please reconnect your account.')
            return redirect('some_google_auth_view')
        
        access_token = social_token.token
        credentials = Credentials(token=access_token)
        
        # Create an authorized HTTP object
        http = google_auth_httplib2.AuthorizedHttp(credentials, http=httplib2.Http())
        
        try:
            logger.info("Attempting to build Google My Business API service...")
            service = build('mybusinessaccountmanagement', 'v1', http=http, cache_discovery=False)
            logger.info("Successfully built Google My Business API service")
       
            try:
                # You need to list accounts first
                accounts = service.accounts().list().execute()
                logger.debug("Accounts response: %s", json.dumps(accounts, indent=2))
                
                if 'accounts' in accounts and accounts['accounts']:
                    account = accounts['accounts'][0]
                    account_name = account['name']  # This will be 'accounts/{account_id}'
                    
                    # Use the account_name to list all locations for the account
                    service = build('mybusinessinformation', 'v1', http=http, cache_discovery=False)
                    locations = service.accounts().locations().list(parent=account_name).execute()
                    logger.debug("Locations response: %s", json.dumps(locations, indent=2))
                    
                    if 'locations' in locations and locations['locations']:
                        location = locations['locations'][0]
                        # Fetch detailed information for the first location
                        location_name = location['name']
                        location_details = service.accounts().locations().get(name=location_name).execute()
                        logger.debug("Location details: %s", json.dumps(location_details, indent=2))
                        
                        return render(request, 'create.html', {'business_info': location_details})
                    else:
                        logger.warning("No business locations found for user %s", request.user.username)
                        messages.warning(request, 'No business locations found for this Google account. You may need to create a Google My Business listing first.')
                        return redirect('create')  # or wherever you want to redirect
                
                else:
                    logger.warning("No Google My Business accounts found for user %s", request.user.username)
                    messages.warning(request, 'No Google My Business accounts found for this user.')
                    return redirect('create')
            
            except HttpError as api_error:
                if api_error.resp.status == 403:
                    logger.warning("Permission denied. The user might not have any business listings. User: %s", request.user.username)
                    messages.warning(request, 'Unable to access business information. You may not have any Google My Business listings, or you may need to grant additional permissions.')
                else:
                    logger.error("API error: %s", api_error, exc_info=True)
                    messages.error(request, f'Error fetching business info: {api_error.reason}')
            
        except HttpError as error:
            logger.error("An HTTP error occurred: %s", error, exc_info=True)
            messages.error(request, f'Error accessing Google My Business API: {error}')
        except RefreshError as refresh_error:
            logger.error("Token refresh error: %s", refresh_error, exc_info=True)
            messages.error(request, 'Your Google token has expired. Please reconnect your account.')
            return redirect('some_google_auth_view')
        except Exception as e:
            logger.error("Error building API service: %s", str(e), exc_info=True)
            messages.error(request, f'Error accessing Google My Business API: {str(e)}')
    
    except SocialAccount.DoesNotExist:
        logger.error("SocialAccount does not exist for user %s", request.user.username)
        messages.error(request, 'Google account not connected.')
    except Exception as e:
        logger.error("Unexpected error: %s", str(e), exc_info=True)
        messages.error(request, f'Error fetching business info: {str(e)}')
    
    return redirect('create')


def index(request): 
    business_list = Business.objects.all().order_by('-created')
    paginator = Paginator(business_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = {
            'businesses': [
                {
                    'name': business.business_name,
                    'city': business.city,
                    'state': business.state,
                    'cuisine': str(business.cuisine),
                    'created': business.created.strftime('%B %d, %Y'),
                    'url': reverse('business_subdirectory', args=[business.business_name])
                } for business in page_obj
            ],
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'num_pages': paginator.num_pages,
            'current_page': page_obj.number
        }
        return JsonResponse(data)

    return render(request, 'index.html', {'page_obj': page_obj})

def custom_logout(request):
    logout(request)
    return JsonResponse({'success': True})


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
def create(request):
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
                cuisine_names = []
            # Combine address components for geocoding
            full_address = f"{new_business.address}, {new_business.city}, {new_business.state} {new_business.zip_code}"

            try:
                # Geocode the address
                geocode_result = gmaps.geocode(full_address)

                if geocode_result:
                    location = geocode_result[0]['geometry']['location']
                    formatted_address = geocode_result[0]['formatted_address']
                    coordinates = f"{location['lat']},{location['lng']}"

                    if Business.verified_business_exists(formatted_address):
                        raise ValidationError("A verified business already exists at this address.")
                    
                    new_business.address = formatted_address

                    new_business.save()
                    # Only add cuisines if there are any
                    if cuisine_names:
                        for cuisine_name in cuisine_names:
                            cuisine_category, created = CuisineCategory.objects.get_or_create(
                                cuisine=cuisine_name
                            )
                            new_business.cuisine.add(cuisine_category)
                    slug = f"{new_business.subdirectory}-home"
                    home_page = SubPage.objects.create(
                        business=new_business,
                        page_type='home',
                        title=f"{new_business.business_name} Home",
                        slug=slug,
                        is_published=True,
                        hero_heading=f"Welcome to {new_business.business_name}",
                        hero_subheading="We're excited to serve you!",
                        show_hero_heading=True,
                        show_hero_subheading=True
                    )
                    messages.success(request, 'business created successfully!')
                    return redirect(reverse('business_subdirectory', kwargs={'business_subdirectory': new_business.subdirectory}))
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

# def get_business_context(business, user, is_preview=False):
#     """Helper function to create consistent context for both views"""
#     # Get subpage information
#     menu_page = SubPage.objects.filter(business=business, page_type='menu').exists()
#     about_page = SubPage.objects.filter(business=business, page_type='about').exists()
#     events_page = SubPage.objects.filter(business=business, page_type='events').exists()
#     specials_page = SubPage.objects.filter(business=business, page_type='specials').exists()
    
#     return {
#         "business_subdirectory": business.subdirectory,
#         "business_details": business,
#         "owner": user == business.owner,
#         "is_verified": business.is_verified,
#         "menu_page": menu_page,
#         "about_page": about_page,
#         "events_page": events_page,
#         "specials_page": specials_page,
#         "is_preview": is_preview
#     }

#feed any page type to this function to get the context for that page
def get_business_context(business, user, page_type='home'):
    """
    Get context for any business subpage
    page_type can be: 'home', 'about', 'menu', 'services', 'products', 'gallery', 'contact'
    """
    # Get the requested subpage and its images
    subpage = SubPage.objects.filter(
        business=business, 
        page_type=page_type
    ).first()

    # Get all published subpages for navigation
    published_pages = SubPage.get_published_subpages(business)

    # Get images for the current subpage
    hero_primary = subpage.get_hero_primary() if subpage else None
    banner_2 = subpage.get_banner_2() if subpage else None
    banner_3 = subpage.get_banner_3() if subpage else None

    # Get menu items if they exist
    menu_items = {
        'exists': Menu.objects.filter(business=business).exists(),
        'featured': Dish.objects.filter(
            menu__business=business, 
            is_special=True
        ).select_related('menu').prefetch_related('images')[:3]
    }

    # Get upcoming events if they exist
    events = {
        'exists': Event.objects.filter(
            events_page__subpage__business=business, 
            date__gte=timezone.now()
        ).exists(),
        'upcoming': Event.objects.filter(
            events_page__subpage__business=business,
            date__gte=timezone.now()
        ).order_by('date')[:2]
    }

    # Get page-specific content
    page_content = {}
    if page_type == 'about':
        about_page = getattr(subpage, 'aboutuspage', None)
        if about_page:
            page_content = {
                'team_members': about_page.team_members.all() if hasattr(about_page, 'team_members') else [],
                'history': about_page.history,
                'mission': about_page.mission,
            }
    elif page_type == 'menu':
        page_content = {
            'menus': Menu.objects.filter(business=business).prefetch_related(
                'courses', 
                'courses__dishes'
            ),
            'specials': Dish.objects.filter(menu__business=business, is_special=True),
        }
    elif page_type == 'events':
        events_page = getattr(subpage, 'eventspage', None)
        if events_page:
            page_content = {
                'upcoming_events': events_page.events.filter(date__gte=timezone.now()).order_by('date'),
                'past_events': events_page.events.filter(date__lt=timezone.now()).order_by('-date'),
            }
    print(business)
    page_data = {
        'business_subdirectory': business.subdirectory,
        'current_page': subpage,
        # Primary Hero Data
        'hero_heading': subpage.hero_heading,
        'hero_subheading': subpage.hero_subheading,
        'hero_button_text': subpage.hero_button_text,
        'hero_button_link': subpage.hero_button_link,
        'hero_layout': subpage.hero_layout,
        'hero_text_align': subpage.hero_text_align,
        'hero_heading_color': subpage.hero_heading_color,
        'hero_subheading_color': subpage.hero_subheading_color,
        'hero_size': subpage.hero_size,
        'show_hero_heading': subpage.show_hero_heading,
        'show_hero_subheading': subpage.show_hero_subheading,
        'show_hero_button': subpage.show_hero_button,
        'hero_heading_font': subpage.hero_heading_font,
        'hero_subheading_font': subpage.hero_subheading_font,
        'hero_heading_size': subpage.hero_heading_size,
        'hero_subheading_size': subpage.hero_subheading_size,
        'hero_primary': {
            'url': hero_primary.image.url if hero_primary else None,
            'alt_text': hero_primary.alt_text if hero_primary else None
        },
        # Button Styles
        'hero_button_bg_color': subpage.hero_button_bg_color,
        'hero_button_text_color': subpage.hero_button_text_color,
        
        # Banner 2 Data
        'banner_2': {
            'heading': subpage.banner_2_heading,
            'subheading': subpage.banner_2_subheading,
            'show_heading': subpage.show_banner_2_heading,
            'show_subheading': subpage.show_banner_2_subheading,
            'heading_font': subpage.banner_2_heading_font,
            'subheading_font': subpage.banner_2_subheading_font,
            'heading_size': subpage.banner_2_heading_size,
            'subheading_size': subpage.banner_2_subheading_size,
            'heading_color': subpage.banner_2_heading_color,
            'subheading_color': subpage.banner_2_subheading_color,
            'button_text': subpage.banner_2_button_text,
            'button_link': subpage.banner_2_button_link,
            'text_align': subpage.banner_2_text_align,
            'button_bg_color': subpage.banner_2_button_bg_color,
            'button_text_color': subpage.banner_2_button_text_color,
            'url': banner_2.image.url if banner_2 else None,
            'alt_text': banner_2.alt_text if banner_2 else None
        },
        
        # Banner 3 Data
        'banner_3': {
            'heading': subpage.banner_3_heading,
            'subheading': subpage.banner_3_subheading,
            'show_heading': subpage.show_banner_3_heading,
            'show_subheading': subpage.show_banner_3_subheading,
            'heading_font': subpage.banner_3_heading_font,
            'subheading_font': subpage.banner_3_subheading_font,
            'heading_size': subpage.banner_3_heading_size,
            'subheading_size': subpage.banner_3_subheading_size,
            'heading_color': subpage.banner_3_heading_color,
            'subheading_color': subpage.banner_3_subheading_color,
            'button_text': subpage.banner_3_button_text,
            'button_link': subpage.banner_3_button_link,
            'text_align': subpage.banner_3_text_align,
            'button_bg_color': subpage.banner_3_button_bg_color,
            'button_text_color': subpage.banner_3_button_text_color,
            'url': banner_3.image.url if banner_3 else None,
            'alt_text': banner_3.alt_text if banner_3 else None
        },
        'is_published': subpage.is_published,
    }

    context = {
        # For JavaScript initialization
        'page_data': page_data,
        # For template rendering
        'business_details': business,
        'business_subdirectory': business.subdirectory,
        # changed to published_pages
        'subpages': published_pages,
        'subpage': subpage,
        'current_page': subpage,
        # Choices/Options for template dropdowns and selectors
        'hero_primary': hero_primary,
        'banner_2': banner_2,
        'banner_3': banner_3,
        'hero_heading_font': subpage.hero_heading_font,
    }
    # context = {
    #     'business_details': {
    #         'business_name': business.business_name,
    #         'subdirectory': business.subdirectory,
    #         'description': business.description,
    #         'navigation_style': business.navigation_style or 'default',
    #         'footer_style': business.footer_style or 'default',
    #         'primary_color': business.primary_color or '#000000',
    #         'secondary_color': business.secondary_color or '#666666',
    #         'text_color': business.text_color or '#000000',
    #         'hover_color': business.hover_color or '#333333',
    #         'menu_items': menu_items,
    #         'events': events,
    #         'contact_info': {
    #             'phone': business.phone_number,
    #             'address': business.address,
    #             'city': business.city,
    #             'state': business.state,
    #             'zip_code': business.zip_code,
    #         }
    #     },
    #     'subpage': subpage,
    #     'page_type': page_type,
    #     'published_pages': published_pages,
    #     'hero_image': hero_primary,
    #     'banner_2': banner_2,
    #     'banner_3': banner_3,
    #     'page_content': page_content,
    #     'user': user,
    #     'is_owner': user == business.owner,
    #     'is_verified': business.is_verified,
    # }

    return context

# new business page view
def business_page(request, business_subdirectory, page_type='home'):
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
        template = "eatery_owner.html" 
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
    
def create_subpage(request, business_subdirectory, page_type):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    business = get_object_or_404(Business, subdirectory=business_subdirectory)
    
    # Check if user is owner
    if request.user != business.owner:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    # Check if subpage already exists
    if SubPage.objects.filter(business=business, page_type=page_type).exists():
        messages.error(request, f'A {page_type} page already exists for this business.')
        return redirect('business_subdirectory', business_subdirectory=business_subdirectory)

    # Create a unique slug by adding a timestamp
    from django.utils import timezone
    timestamp = timezone.now().strftime('%Y%m%d-%H%M%S')
    unique_slug = f"{business.subdirectory}-{page_type}-{timestamp}"

    # Create the subpage
    subpage = SubPage.objects.create(
        business=business,
        page_type=page_type,
        title=f"{business.business_name} {page_type.title()}",
        slug=unique_slug,
        is_published=True
    )

    # Create the corresponding page content based on type
    if page_type == 'menu':
        Menu.objects.create(
            business=business,
            name=f"{business.business_name} Menu",
            subpage=subpage
        )
    elif page_type == 'about':
        AboutUsPage.objects.create(
            subpage=subpage,
            content=""
        )
    elif page_type == 'events':
        EventsPage.objects.create(
            subpage=subpage
        )
    elif page_type == 'specials':
        SpecialsPage.objects.create(
            subpage=subpage
        )

    messages.success(request, f'{page_type.title()} page created successfully!')
    # Redirect to the appropriate page
    return redirect(reverse(page_type, kwargs={'business_subdirectory': business_subdirectory}))

def menu(request, business_subdirectory):
    business = get_object_or_404(Business, subdirectory=business_subdirectory)
    
    # First get the menu subpage
    menu_subpage = get_object_or_404(SubPage, business=business, page_type='menu')
    
    try:
        # Then get the menu associated with this subpage
        menu = Menu.objects.get(subpage=menu_subpage)
        courses = Course.objects.filter(menu=menu).order_by('order')
        dishes = Dish.objects.filter(menu=menu)
    except Menu.DoesNotExist:
        # If no menu exists yet, create one
        menu = Menu.objects.create(
            business=business,
            name=f"{business.business_name} Menu",
            subpage=menu_subpage
        )
        courses = []
        dishes = []

    course_options = [
        'Appetizers',
        'Lunch',
        'Entrees',
        'Main Courses',
        'Soup and Salad',
        'Salads',
        'Desserts',
        'Drinks',
        'Specials',
        'Dinner',
        'Breakfast',
        'Brunch',
        'Kids Menu',
        'Beverages',
        'Vegan',
        'Gluten Free',
        'Dairy Free',
        'Nut Free',
        'Halal',
        'Kosher'
    ]
    
    context = {
        "business_subdirectory": business_subdirectory,
        "business_details": business,
        "courses": courses,
        "dishes": dishes,
        "course_options": course_options,
        "owner": request.user == business.owner,
        "is_verified": business.is_verified,
        "menu": menu,
    }

    if request.method != "GET":
        return JsonResponse({"error": "GET request required."}, status=400)

    if not business.is_verified and request.user != business.owner:
        return render(request, "business_under_construction.html", context)
        
    elif request.user != business.owner:
        return render(request, "visitor_pages/menu.html", context)
    
    else:
        return render(request, "owner_subpages/menu.html", context)


def about(request, business_subdirectory):
    business = get_object_or_404(Business, subdirectory=business_subdirectory)
    
    # First get the subpage for this business
    about_subpage = get_object_or_404(SubPage, business=business, page_type='about')
    
    # Then get the about page associated with this subpage
    about_page = get_object_or_404(AboutUsPage, subpage=about_subpage)
    
    context = {
        "business_details": business,
        "business_subdirectory": business_subdirectory,
        "about_page": about_page,
        "owner": request.user == business.owner,
    }

    if not business.is_verified and request.user != business.owner:
        return render(request, "business_under_construction.html", context)
        
    elif request.user != business.owner:
        return render(request, "visitor_pages/about.html", context)
    
    else:
        return render(request, "owner_subpages/about.html", context)

def specials(request, business_subdirectory):
    business = get_object_or_404(Business, subdirectory=business_subdirectory)
    
    # First get the subpage for this business
    specials_subpage = get_object_or_404(SubPage, business=business, page_type='specials')
    
    # Then get the specials page associated with this subpage
    specials_page = get_object_or_404(SpecialsPage, subpage=specials_subpage)
    
    context = {
        "business_details": business,
        "business_subdirectory": business_subdirectory,
        "specials_page": specials_page,
        "owner": request.user == business.owner,
    }

    if not business.is_verified and request.user != business.owner:
        return render(request, "business_under_construction.html", context)
        
    elif request.user != business.owner:
        return render(request, "visitor_pages/specials.html", context)
    
    else:
        return render(request, "owner_subpages/specials.html", context)
    
def events(request, business_subdirectory):
    business = get_object_or_404(Business, subdirectory=business_subdirectory)
    
    # First get the subpage for this business
    events_subpage = get_object_or_404(SubPage, business=business, page_type='events')
    
    # Then get the events page associated with this subpage
    events_page = get_object_or_404(EventsPage, subpage=events_subpage)
    
    context = {
        "business_details": business,
        "business_subdirectory": business_subdirectory,
        "events_page": events_page,
        "owner": request.user == business.owner,
    }

    if not business.is_verified and request.user != business.owner:
        return render(request, "business_under_construction.html", context)
        
    elif request.user != business.owner:
        return render(request, "visitor_pages/events.html", context)
    
    else:
        return render(request, "owner_subpages/events.html", context)

@login_required
def new_dish(request, business_name):
    if request.method == "GET":
        return render(request, "newdish.html", {"new_dish" : DishSubmit()})
    if request.method == "POST":
        form = Dish(request.POST)
        user = request.user
        if form.is_valid():
            name = form.cleaned_data["name"]
            price = form.cleaned_data["price"]
            recipe_owner = business_name
            image_url = form.cleaned_data["image_url"]
            course = form.cleaned_data["course"]
            description = form.cleaned_data["description"]
        else:
            print(form.errors)
            return render(request, "newdish.html", {"new_dish" : DishSubmit()})
        new = Dish(name=name, price=price, image_url=image_url, course=course, description=description, recipe_owner=recipe_owner)
        new.save()
        messages.add_message(request, messages.INFO, f"'{name}' successfully added to menu")
        return HttpResponseRedirect(reverse('business_subdirectory', kwargs={"business_name": business_name}))

@ensure_csrf_cookie
def add_course(request, business_subdirectory):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    business = get_object_or_404(Business, subdirectory=business_subdirectory)
    
    # Check if user is owner
    if request.user != business.owner:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    try:
        data = json.loads(request.body)
        course_name = data.get('course_name')
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    if not course_name:
        return JsonResponse({"error": "Course name is required"}, status=400)

    # First try to get menu through subpage
    try:
        menu_subpage = SubPage.objects.get(business=business, page_type='menu')
        menu = Menu.objects.get(subpage=menu_subpage)
    except (SubPage.DoesNotExist, Menu.DoesNotExist):
        # If that fails, try to get menu directly through business
        menu = get_object_or_404(Menu, business=business)

    # Create new course
    highest_order = Course.objects.filter(menu=menu).aggregate(Max('order'))['order__max'] or 0
    course = Course.objects.create(
        menu=menu,
        name=course_name,
        order=highest_order + 1
    )

    return JsonResponse({
        "message": "Course added successfully",
        "course_id": course.id
    })

@csrf_exempt
@login_required
def add_dish(request, business_subdirectory):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    try:
        data = json.loads(request.body)
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        
        # Check if user is owner
        if request.user != business.owner:
            return JsonResponse({"error": "Unauthorized"}, status=403)

        # Get the menu
        menu_subpage = get_object_or_404(SubPage, business=business, page_type='menu')
        menu = get_object_or_404(Menu, subpage=menu_subpage)

        # Get or create the course
        course_name = data.get("course", "")
        course = Course.objects.get(menu=menu, name=course_name)

        dish_name = data.get("name", "").strip()
        if Dish.objects.filter(course=course, name__iexact=dish_name).exists():
            return JsonResponse({
                "error": f"A dish with the name '{dish_name}' already exists in the {course_name} course."
            }, status=400)
        
        image_data = data.get('image')
        image = None
        if image_data and 'base64,' in image_data:
            # Split the base64 string
            format, imgstr = image_data.split('base64,')
            # Get the file extension
            ext = format.split('/')[-1].split(';')[0]
            # Generate filename
            filename = f"{business.subdirectory}_{data.get('name')}_{uuid.uuid4().hex[:6]}.{ext}"
            
            # Create ContentFile from base64 data
            image = ContentFile(base64.b64decode(imgstr), name=filename)

        # Create new dish
        new_dish = Dish.objects.create(
            menu=menu,
            name=data.get("name", ""),
            description=data.get("description", ""),
            price=data.get("price", ""),
            image=image,
            course=course
        )

        return JsonResponse({
            "message": "Dish added successfully",
            "dish_id": new_dish.id,
            "image_url": new_dish.image.url if new_dish.image else ""
        }, status=201)

    except Course.DoesNotExist:
        return JsonResponse({
            "error": f"Course '{course_name}' not found"
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            "error": "Invalid JSON"
        }, status=400)
    except IntegrityError:
        return JsonResponse({
            "error": "A dish with this name already exists in your menu."
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "error": str(e)
        }, status=400)

def search(request, position, distance):
    if request.method != "GET":
        return JsonResponse({"error" : "GET request required."}, status=400)
    if distance == "Walk":
        distance_lat = .03
        distance_lon = .04
    if distance == "Bike":
        distance_lat = .075
        distance_lon = .1
    if distance == "Drive":
        distance_lat = .225
        distance_lon = .3
    latitude = position.split(", ")[0]
    latitude = float(latitude)
    longitude = position.split(", ")[1]
    longitude = float(longitude)
    distance_plus_lat = latitude + distance_lat
    distance_minus_lat = latitude - distance_lat
    distance_plus_lon = longitude + distance_lon
    distance_minus_lon = longitude - distance_lon
    business_list = Business.objects.all()
    businesss_nearby = []
    test_dict = []
    for eatery in business_list:
        coordinates = str(eatery.geolocation)
        eatery_latitude = float(coordinates.split(",")[0])
        eatery_longitude = float(coordinates.split(",")[1])
        if distance_plus_lat > eatery_latitude > distance_minus_lat and distance_plus_lon > eatery_longitude > distance_minus_lon:
            between_locations = round(geopy.distance.distance(position, coordinates).miles, 2)
            businesss_nearby.append(eatery)
            e = {
                "eatery": eatery.cuisine.cuisine,
                "name": eatery.business_name,
                "address": eatery.address,
                "city": eatery.city,
                "state": eatery.state,
                "description": eatery.description,
                "between": between_locations,
                "cuisine": eatery.cuisine.cuisine
            }
            test_dict.append(e)
    return JsonResponse([localbusiness for localbusiness in test_dict], safe=False)

def filter(request, place):
    if request.method != "GET":
        return JsonResponse({"error" : "GET request required."}, status=400)
    location_businesss = Business.objects.filter(city__icontains = place)
    return JsonResponse([localEatery.serialize() for localEatery in location_businesss], safe=False)

@csrf_exempt
@login_required
def edit_dish(request, business_subdirectory, dishid):
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)
    
    try:
        dish = Dish.objects.get(id=dishid)
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        
        # Verify owner
        if request.user != business.owner:
            return JsonResponse({"error": "Unauthorized"}, status=403)
            
        data = json.loads(request.body)
        new_name = data.get('name', '').strip()

        # Check if new name already exists in this course (excluding current dish)
        if new_name.lower() != dish.name.lower() and \
           Dish.objects.filter(course=dish.course, name__iexact=new_name).exists():
            return JsonResponse({
                "error": f"A dish with the name '{new_name}' already exists in the {dish.course.name} course."
            }, status=400)
                
        # Update dish fields
        dish.name = data.get('name', dish.name)
        dish.price = data.get('price', dish.price)
        dish.description = data.get('description', dish.description)

        # Handle image data
        image_data = data.get('image')
        if image_data and 'base64,' in image_data:
            # Split the base64 string
            format, imgstr = image_data.split('base64,')
            # Get the file extension
            ext = format.split('/')[-1].split(';')[0]
            # Generate filename
            filename = f"{business.subdirectory}_{dish.name}_{uuid.uuid4().hex[:6]}.{ext}"
            
            # Create ContentFile from base64 data
            image = ContentFile(base64.b64decode(imgstr), name=filename)
            dish.image = image

        dish.save()
        
        return JsonResponse({
            "message": "Dish updated successfully",
            "dish_id": dishid,
            "image_url": dish.image.url if dish.image else ""
        }, status=200)
        
    except Dish.DoesNotExist:
        return JsonResponse({"error": "Dish does not exist."}, status=404)
    except IntegrityError:
        return JsonResponse({
            "error": "A dish with this name already exists in your menu."
        }, status=400)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
@login_required
def delete_dish(request, dishid):
    try:
        dish = Dish.objects.get(id=dishid)
        
        # Add owner verification
        if request.user != dish.menu.subpage.business.owner:
            return JsonResponse({"error": "Unauthorized"}, status=403)
            
        if request.method != "DELETE":  # Changed to DELETE method
            return JsonResponse({"error": "DELETE request required."}, status=400)
            
        dish.delete()
        return JsonResponse({
            "message": "Dish deleted successfully",
            "dish_id": dishid
        }, status=200)
        
    except Dish.DoesNotExist:
        return JsonResponse({"error": "Dish does not exist."}, status=404)

@csrf_exempt
@login_required
def delete_course(request, business_subdirectory, courseid):
    if request.method != "DELETE":
        return JsonResponse({"error": "DELETE request required."}, status=400)
    
    try:
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        
        # Check if user is owner
        if request.user != business.owner:
            return JsonResponse({"error": "Unauthorized"}, status=403)

        course = get_object_or_404(Course, id=courseid)
        
        # Verify the course belongs to this Business's menu
        if course.menu.subpage.business != business:
            return JsonResponse({"error": "Course not found."}, status=404)

        # Delete the course (this will cascade delete all associated dishes)
        course.delete()

        return JsonResponse({
            "message": "Course and all associated dishes deleted successfully"
        }, status=200)

    except Exception as e:
        return JsonResponse({
            "error": str(e)
        }, status=400)


def get_business(request, business_id):
    try:
        business_obj = Business.objects.get(id=business_id)
        return JsonResponse(business_obj.serialize())
    except Business.DoesNotExist:
        return JsonResponse({"error": "Business not found"}, status=404)

def get_dish(request, dish_id):
    try:
        dish_obj = Dish.objects.get(id=dish_id)
        return JsonResponse(dish_obj.serialize())
    except Dish.DoesNotExist:
        return JsonResponse({"error": "Dish not found"}, status=404)

def get_cuisine_categories(request):
    categories = CuisineCategory.objects.all()
    return JsonResponse([category.serialize() for category in categories], safe=False)

@login_required
def upload_image(request, model_name, object_id):
    if model_name not in ['business', 'dish']:
        return HttpResponseBadRequest("Invalid model type")

    model = Business if model_name == 'business' else Dish
    obj = get_object_or_404(model, id=object_id)

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.uploaded_by = request.user
            image.content_type = ContentType.objects.get_for_model(obj)
            image.object_id = obj.id
            image.save()
            return redirect('object_detail', model_name=model_name, object_id=object_id)
    else:
        form = ImageUploadForm()

    return render(request, 'upload_image.html', {'form': form, 'object': obj})


def update_course_description(request, business_subdirectory, course_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    try:
        course = Course.objects.get(id=course_id)
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        
        # Verify owner
        if request.user != business.owner:
            return JsonResponse({"error": "Unauthorized"}, status=403)
            
        data = json.loads(request.body)
        course.description = data.get('description', '').strip()
        course.save()
        
        return JsonResponse({
            "message": "Course description updated successfully",
            "course_id": course_id
        }, status=200)
        
    except Course.DoesNotExist:
        return JsonResponse({"error": "Course does not exist."}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    
def update_course_note(request, business_subdirectory, course_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    try:
        course = Course.objects.get(id=course_id)
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        
        # Verify owner
        if request.user != business.owner:
            return JsonResponse({"error": "Unauthorized"}, status=403)
            
        data = json.loads(request.body)
        course.note = data.get('note', '').strip()
        course.save()
        
        return JsonResponse({
            "message": "Course note updated successfully",
            "course_id": course_id
        }, status=200)
        
    except Course.DoesNotExist:
        return JsonResponse({"error": "Course does not exist."}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    

@require_http_methods(["GET", "POST", "DELETE"])
def side_options(request, business_subdirectory, id):
    """
    Handles all side option operations:
    GET with course_id: Returns all side options for a course
    GET with side_id: Returns a specific side option
    POST with course_id: Creates a new side option
    POST with side_id: Updates an existing side option
    DELETE with side_id: Deletes a side option
    """
    try:
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        if request.user != business.owner:
            return JsonResponse({"error": "Unauthorized"}, status=403)

        # GET request handling
        if request.method == "GET":
            try:
                # Try to get a specific side option
                side = SideOption.objects.get(id=id)
                return JsonResponse({
                    'id': side.id,
                    'name': side.name,
                    'description': side.description,
                    'price': str(side.price),
                    'is_premium': side.is_premium,
                    'course_id': side.course.id
                })
            except SideOption.DoesNotExist:
                # If not found, assume id is course_id and return all side options
                course = get_object_or_404(Course, id=id)
                side_options = course.side_options.all()
                return JsonResponse([{
                    'id': side.id,
                    'name': side.name,
                    'description': side.description,
                    'price': str(side.price),
                    'is_premium': side.is_premium
                } for side in side_options], safe=False)

        # POST request handling
        elif request.method == "POST":
            data = json.loads(request.body)
            
            try:
                # Try to get existing side option (update case)
                side = SideOption.objects.get(id=id)
                side.name = data.get('name', side.name)
                side.description = data.get('description', side.description)
                side.is_premium = data.get('is_premium', side.is_premium)
                side.price = data.get('price', side.price)
                side.save()
                course = side.course
            except SideOption.DoesNotExist:
                # If not found, create new side option
                course = get_object_or_404(Course, id=id)
                side = SideOption.objects.create(
                    course=course,
                    name=data.get('name'),
                    description=data.get('description', ''),
                    is_premium=data.get('is_premium', False),
                    price=data.get('price', 0)
                )

            # Get all side options for the course and return them
            side_options = course.side_options.all()
            return JsonResponse({
                'message': 'Side option saved successfully',
                'course_id': course.id,
                'side_options': [{
                    'id': side.id,
                    'name': side.name,
                    'description': side.description,
                    'price': str(side.price),
                    'is_premium': side.is_premium,
                    'course_id': course.id
                } for side in side_options]
            })

        # DELETE request handling
        elif request.method == "DELETE":
            side = get_object_or_404(SideOption, id=id)
            course_id = side.course.id
            side.delete()
            return JsonResponse({
                'message': 'Side option deleted successfully',
                'course_id': course_id
            })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

@login_required
def edit_layout(request, business_subdirectory):
    try:
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        if request.user != business.owner:
            messages.error(request, "You don't have permission to access this page.")  # Optional: add an error message
            return redirect('index')  # Replace 'index' with your index URL name

        # Get or create subpages for each type
        current_page = 'home'
        available_pages = []
        for page_type, label in SubPage.PAGE_TYPES:
            available_pages.append(page_type)
        current_subpage = SubPage.objects.filter(
            business=business,
            page_type=current_page
        ).first()

        published_pages = SubPage.get_published_subpages(business)
        print('published_pages', published_pages)
        existing_page_types = set([page.get('page_type') for page in published_pages])
        print('existing_page_types', existing_page_types)
        existing_page_types.add(current_page)  # Add current page to existing set
        
        available_pages = []
        for page_type, label in SubPage.PAGE_TYPES:
            if page_type not in existing_page_types:
                available_pages.append({
                    'page_type': page_type,
                    'label': label
                })
        hero_primary = current_subpage.get_hero_primary()
        banner_2 = current_subpage.get_banner_2()
        banner_3 = current_subpage.get_banner_3()
        page_data = {
            'business_subdirectory': business_subdirectory,
            'current_page': current_page,
            # Primary Hero Data
            'hero_heading': current_subpage.hero_heading,
            'hero_subheading': current_subpage.hero_subheading,
            'hero_button_text': current_subpage.hero_button_text,
            'hero_button_link': current_subpage.hero_button_link,
            'hero_layout': current_subpage.hero_layout,
            'hero_text_align': current_subpage.hero_text_align,
            'hero_heading_color': current_subpage.hero_heading_color,
            'hero_subheading_color': current_subpage.hero_subheading_color,
            'hero_size': current_subpage.hero_size,
            'show_hero_heading': current_subpage.show_hero_heading,
            'show_hero_subheading': current_subpage.show_hero_subheading,
            'show_hero_button': current_subpage.show_hero_button,
            'hero_heading_font': current_subpage.hero_heading_font,
            'hero_subheading_font': current_subpage.hero_subheading_font,
            'hero_heading_size': current_subpage.hero_heading_size,
            'hero_subheading_size': current_subpage.hero_subheading_size,
            'hero_primary': {
                'url': hero_primary.image.url if hero_primary else None,
                'alt_text': hero_primary.alt_text if hero_primary else None
            },
            # Button Styles
            'hero_button_bg_color': current_subpage.hero_button_bg_color,
            'hero_button_text_color': current_subpage.hero_button_text_color,
            
            # Banner 2 Data
            'banner_2': {
                'heading': current_subpage.banner_2_heading,
                'subheading': current_subpage.banner_2_subheading,
                'show_heading': current_subpage.show_banner_2_heading,
                'show_subheading': current_subpage.show_banner_2_subheading,
                'heading_font': current_subpage.banner_2_heading_font,
                'subheading_font': current_subpage.banner_2_subheading_font,
                'heading_size': current_subpage.banner_2_heading_size,
                'subheading_size': current_subpage.banner_2_subheading_size,
                'heading_color': current_subpage.banner_2_heading_color,
                'subheading_color': current_subpage.banner_2_subheading_color,
                'button_text': current_subpage.banner_2_button_text,
                'button_link': current_subpage.banner_2_button_link,
                'text_align': current_subpage.banner_2_text_align,
                'button_bg_color': current_subpage.banner_2_button_bg_color,
                'button_text_color': current_subpage.banner_2_button_text_color,
                'url': banner_2.image.url if banner_2 else None,
                'alt_text': banner_2.alt_text if banner_2 else None
            },
            
            # Banner 3 Data
            'banner_3': {
                'heading': current_subpage.banner_3_heading,
                'subheading': current_subpage.banner_3_subheading,
                'show_heading': current_subpage.show_banner_3_heading,
                'show_subheading': current_subpage.show_banner_3_subheading,
                'heading_font': current_subpage.banner_3_heading_font,
                'subheading_font': current_subpage.banner_3_subheading_font,
                'heading_size': current_subpage.banner_3_heading_size,
                'subheading_size': current_subpage.banner_3_subheading_size,
                'heading_color': current_subpage.banner_3_heading_color,
                'subheading_color': current_subpage.banner_3_subheading_color,
                'button_text': current_subpage.banner_3_button_text,
                'button_link': current_subpage.banner_3_button_link,
                'text_align': current_subpage.banner_3_text_align,
                'button_bg_color': current_subpage.banner_3_button_bg_color,
                'button_text_color': current_subpage.banner_3_button_text_color,
                'url': banner_3.image.url if banner_3 else None,
                'alt_text': banner_3.alt_text if banner_3 else None
            },
            'is_published': current_subpage.is_published,
        }

        context = {
            # For JavaScript initialization
            'page_data': page_data,
            # For template rendering
            'business_details': business,
            'business_subdirectory': business_subdirectory,
            # changed to published_pages
            'subpages': published_pages,
            'subpage': current_subpage,
            'current_page': current_page,
            'available_pages': available_pages,
            # Choices/Options for template dropdowns and selectors
            'hero_choices': SubPage.HERO_CHOICES,
            'nav_styles': business.NAV_CHOICES,
            'footer_styles': business.FOOTER_CHOICES,
            'text_align_choices': SubPage.TEXT_ALIGN_CHOICES,
            'font_choices': get_font_choices(),
            'heading_sizes': get_font_sizes('heading'),
            'subheading_sizes': get_font_sizes('subheading'),
            'hero_size_choices': SubPage.HERO_SIZE_CHOICES,
            'hero_primary': hero_primary,
            'banner_2': banner_2,
            'banner_3': banner_3,
            'preview_mode': True,
            'hero_heading_font': current_subpage.hero_heading_font,
        }
        
        return render(request, "edit_layout.html", context)
        
    except Exception as e:
        import traceback
        logger.error(f"Error in edit_layout: {str(e)}\n{traceback.format_exc()}")

        return HttpResponse(f"Error loading layout editor: {str(e)}", status=500)


@require_POST
def update_layout(request, business_subdirectory):
    try:
        data = json.loads(request.body)
        print("Received data:", data)
        
        field_type = data.get('fieldType')
        field_name = data.get('fieldName')
        value = data.get('value')
        page_type = data.get('page_type')
        is_global = data.get('isGlobal', False)
        return_preview = data.get('return_preview', False)

        # Get the business and subpage
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        subpage = get_object_or_404(SubPage, business=business, page_type=page_type)

        # Handle brand color updates
        if field_type == 'color' and field_name in ['primary', 'secondary', 'text-color', 'hover-color']:
            color_field_map = {
                'primary': 'primary_color',
                'secondary': 'secondary_color',
                'text-color': 'text_color',
                'hover-color': 'hover_color'
            }
            actual_field_name = color_field_map.get(field_name)
            if actual_field_name:
                setattr(business, actual_field_name, value)
                business.save()
        elif is_global:  # Add this block for global components
            # These are business-level settings
            setattr(business, field_name, value)
            business.save()
        else:
            # Handle regular subpage updates
            setattr(subpage, field_name, value)
            print(field_name, value)
            subpage.save()

        response_data = {'success': True}

        if return_preview:
            # First render the content template
            content_html = render_to_string(f'components/preview/{page_type}.html', {
                'business_details': business,
                'subpage': subpage,
                'hero_primary': subpage.get_hero_primary(),
                'banner_2': subpage.get_banner_2(),
                'banner_3': subpage.get_banner_3(),
                'preview_mode': True,
                'current_page': page_type,
            })

            # Then render the navigation
            nav_html = render_to_string(
                f'components/navigation/top-nav/{business.navigation_style}.html',
                {
                    'business_details': business,
                    'subdirectory': business_subdirectory,
                    'primary_color': business.primary_color,
                    'secondary_color': business.secondary_color,
                    'text_color': business.text_color,
                    'hover_color': business.hover_color,
                }
            )

            # Render the footer
            footer_html = render_to_string(
                f'components/footer/{business.footer_style}.html',
                {
                    'business_details': business,
                    'primary_color': business.primary_color,
                    'secondary_color': business.secondary_color,
                    'text_color': business.text_color,
                    'hover_color': business.hover_color,
                }
            )

            # Combine all parts in the preview layout
            preview_html = render_to_string('components/preview/preview_layout.html', {
                'navigation_html': nav_html,
                'content_html': content_html,
                'footer_html': footer_html,
                'business_details': business,
                'subpage': subpage,
                'current_page': page_type,
                'preview_mode': True,
                'hero_primary': subpage.get_hero_primary(),
                'banner_2': subpage.get_banner_2(),
                'banner_3': subpage.get_banner_3(),
                'business_subdirectory': business_subdirectory,
            })
            response_data['preview_html'] = preview_html

        return JsonResponse(response_data)

    except Exception as e:
        print(f"Error in update_layout: {str(e)}")
        print(f"Request body: {request.body}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required
def preview_page(request, business_subdirectory, page_type):
    try:
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        if request.user != business.owner:
            return HttpResponseForbidden()
            
        subpage = SubPage.objects.get(
            business=business,
            page_type=page_type
        )
        
        # Add debug logging
        logger.debug(f"Loading preview for {business_subdirectory}, page type: {page_type}")
        
        # Get all hero images
        hero_primary = subpage.get_hero_primary()
        banner_2 = subpage.get_banner_2()
        banner_3 = subpage.get_banner_3()
        
        # Debug log the images
        logger.debug(f"Hero images found: Primary={hero_primary}, Banner2={banner_2}, Banner3={banner_3}")
        
        context = {
            'business_details': business,
            'subpage': subpage,
            'hero_primary': hero_primary,
            'banner_2': banner_2,
            'banner_3': banner_3,
            'preview_mode': True,
            'business_subdirectory': business_subdirectory,
            'debug': True,  # Make sure debug is True
            # Add specific color context
            'primary_color': business.primary_color,
            'secondary_color': business.secondary_color,
            'text_color': business.text_color,
            'hover_color': business.hover_color,
            'navigation_style': business.navigation_style,
            'footer_style': business.footer_style,
            'current_page': page_type,
            'is_published': subpage.is_published
        }
        
        # Map page_type to template name
        template_mapping = {
            'home': 'home',
            'about': 'about',
            'menu': 'menu',
            'contact': 'contact',
            'gallery': 'gallery',
            'events': 'events',
            'catering': 'catering',
            'order': 'order',
            'reservations': 'reservations'
        }
        
        # Get the template name from mapping or default to home
        template_page = template_mapping.get(page_type, 'home')
        template_name = f'visitor_pages/{template_page}.html'
        
        logger.debug(f"Using template: {template_name}")
        
        return render(request, 'components/preview/preview_layout.html', context)
        
    except Exception as e:
        logger.error(f"Error in preview_page: {str(e)}")
        logger.exception("Full traceback:")
        return HttpResponse(f"Error loading preview: {str(e)}", status=500)
    
@login_required
def get_page_data(request, business_subdirectory, page_type):
    try:
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        if request.user != business.owner:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
            
        subpage = get_object_or_404(SubPage, business=business, page_type=page_type)
        
        # Get all images
        hero_primary = subpage.get_hero_primary()
        banner_2 = subpage.get_banner_2()
        banner_3 = subpage.get_banner_3()
        
        # Debug log to verify we have the images
        logger.debug(f"Images found - Primary: {hero_primary}, Banner2: {banner_2}, Banner3: {banner_3}")

        # def get_safe_image_url(image_obj):
        #     if image_obj and hasattr(image_obj, 'image'):
        #         try:
        #             image_url = image_obj.image.url
        #             logger.debug(f"Got image URL: {image_url}")
        #             return image_url
        #         except Exception as e:
        #             logger.error(f"Error getting image URL: {e}")
        #             return None
        #     return None
        
        data = {
            'subpage_id': subpage.id,
            'hero_heading': subpage.hero_heading,
            'hero_subheading': subpage.hero_subheading,
            'hero_button_text': subpage.hero_button_text,
            'hero_layout': subpage.hero_layout,
            'hero_text_align': subpage.hero_text_align,
            'hero_heading_color': subpage.hero_heading_color,
            'hero_subheading_color': subpage.hero_subheading_color,
            'hero_button_link': subpage.hero_button_link,
            'hero_size': subpage.hero_size,
            'is_published': subpage.is_published,
            'hero_primary': {
                'url': hero_primary.image.url if hero_primary else None,
                'alt_text': hero_primary.alt_text if hero_primary else None
            },
            # 'hero_image': {
            #     'url': get_safe_image_url(hero_primary),
            #     'alt': 'hero_primary'
            # },
            # 'banner_2': {
            #     'url': get_safe_image_url(banner_2),
            #     'alt': 'banner_2'
            # },
            # 'banner_3': {
            #     'url': get_safe_image_url(banner_3),
            #     'alt': 'banner_3'
            # },
            # 'images': {
            #     'hero_primary': {
            #         'url': get_safe_image_url(hero_primary),
            #         'alt': 'hero_primary'
            #     },
            #     'banner_2': {
            #         'url': get_safe_image_url(banner_2),
            #         'alt': 'banner_2'
            #     },
            #     'banner_3': {
            #         'url': get_safe_image_url(banner_3),
            #         'alt': 'banner_3'
            #     }
            # },
            'banner_2': {
                'heading': subpage.banner_2_heading,
                'subheading': subpage.banner_2_subheading,
                'show_heading': subpage.show_banner_2_heading,
                'show_subheading': subpage.show_banner_2_subheading,
                'heading_font': subpage.banner_2_heading_font,
                'subheading_font': subpage.banner_2_subheading_font,
                'heading_size': subpage.banner_2_heading_size,
                'subheading_size': subpage.banner_2_subheading_size,
                'heading_color': subpage.banner_2_heading_color,
                'subheading_color': subpage.banner_2_subheading_color,
                'button_text': subpage.banner_2_button_text,
                'button_link': subpage.banner_2_button_link,
                'button_bg_color': subpage.banner_2_button_bg_color,
                'button_text_color': subpage.banner_2_button_text_color,
                'button_size': subpage.banner_2_button_size,
                'show_button': subpage.show_banner_2_button,
                'text_align': subpage.banner_2_text_align,
                'url': banner_2.image.url if banner_2 else None,
                'alt_text': banner_2.alt_text if banner_2 else None

            },
            'banner_3': {
                'heading': subpage.banner_3_heading,
                'subheading': subpage.banner_3_subheading,
                'show_heading': subpage.show_banner_3_heading,
                'show_subheading': subpage.show_banner_3_subheading,
                'heading_font': subpage.banner_3_heading_font,
                'subheading_font': subpage.banner_3_subheading_font,
                'heading_size': subpage.banner_3_heading_size,
                'subheading_size': subpage.banner_3_subheading_size,
                'heading_color': subpage.banner_3_heading_color,
                'subheading_color': subpage.banner_3_subheading_color,
                'button_text': subpage.banner_3_button_text,
                'button_link': subpage.banner_3_button_link,
                'button_bg_color': subpage.banner_3_button_bg_color,
                'button_text_color': subpage.banner_3_button_text_color,
                'button_size': subpage.banner_3_button_size,
                'show_button': subpage.show_banner_3_button,
                'text_align': subpage.banner_3_text_align,
                'url': banner_3.image.url if banner_3 else None,
                'alt_text': banner_3.alt_text if banner_3 else None
            }
        }
        logger.debug(f"get_page_data data: {data}")
        return JsonResponse(data)
        
    except Exception as e:
        logger.error(f"Error in get_page_data: {str(e)}")
        logger.exception("Full traceback:")
        return JsonResponse({'error': str(e)}, status=500)
        
@login_required
def preview_component(request, business_subdirectory):
    try:
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        if request.user != business.owner:
            return HttpResponseForbidden()

        # Get data from request
        data = json.loads(request.body)
        component = data.get('component')
        value = data.get('value')
        page_type = data.get('page_type', 'home')

        # Get the subpage
        subpage = get_object_or_404(SubPage, business=business, page_type=page_type)

        # Determine which template and context to use based on the component
        template_name = None
        context = {
            'business_details': business,
            'subpage': subpage,
            'business_subdirectory': business_subdirectory,
        }

        # Handle different component types
        if component.startswith('hero_'):
            template_name = f"components/hero/{subpage.hero_layout}.html"
            # Add hero-specific context if needed
            context.update({
                'hero_primary': subpage.get_hero_primary(),
                'banner_2': subpage.get_banner_2(),
                'banner_3': subpage.get_banner_3(),
            })
        elif component == 'navigation':
            template_name = f"components/navigation/top-nav/{business.navigation_style}.html"
            context.update({
                'menu_page': True,
                'about_page': True,
                'events_page': True,
            })
        # Add more component types as needed

        if not template_name:
            return JsonResponse({
                'success': False,
                'error': f'Unknown component: {component}'
            }, status=400)

        try:
            html = render_to_string(template_name, context)
            return JsonResponse({
                'success': True,
                'html': html,
                'component': component
            })
        except Exception as e:
            logger.error(f"Template rendering error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Template rendering error: {str(e)}'
            }, status=500)

    except Exception as e:
        logger.error(f"Preview component error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def preview_navigation(request, business_subdirectory, style):
    try:
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        if request.user != business.owner:
            return HttpResponseForbidden()
        
        template_name = f"components/navigation/top-nav/{style}.html"
        context = {
            'business_details': business,
            'business_subdirectory': business_subdirectory,
            'menu_page': True,
            'about_page': True,
            'events_page': True,
        }
        
        html = render_to_string(template_name, context)
        return HttpResponse(html)
            
    except Exception as e:
        logger.error(f"Error in preview_navigation: {str(e)}")
        return HttpResponse(f"Error: {str(e)}", status=500)

def update_global_component(request, business_subdirectory):
    try:
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        if request.user != business.owner:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        data = json.loads(request.body)
        component = data.get('component')
        style = data.get('style')
        page_type = request.GET.get('page_type')

        if not page_type:
            return JsonResponse({'error': 'Page type is required'}, status=400)
        try:
            subpage = SubPage.objects.get(business=business, page_type=page_type)
        except SubPage.DoesNotExist:
            return JsonResponse({'error': f'Page {page_type} not found'}, status=404)

        logger.debug(f"Updating component: {component} with style: {style} for page: {page_type}")

        # Map components to their model, field, and choices
        component_map = {
            # Global components (Business model)
            'navigation': {
                'model': business,
                'field': 'navigation_style',
                'choices': business.NAV_CHOICES,
                'instance': business
            },
            'main_font': {
                'model': business,
                'field': 'main_font',
                'choices': get_font_choices(),  # From your constants.py
                'instance': business
            },
            'hero_layout': {
                'model': SubPage,
                'field': 'hero_layout',
                'choices': SubPage.HERO_CHOICES,
                'instance': SubPage.objects.get(business=business, page_type=page_type)
            },
            'hero_heading_font': {
                'model': SubPage,
                'field': 'hero_heading_font',
                'choices': get_font_choices(),
                'instance': SubPage.objects.get(business=business, page_type=page_type)
            },
            'hero_subheading_font': {
                'model': SubPage,
                'field': 'hero_subheading_font',
                'choices': get_font_choices(),
                'instance': SubPage.objects.get(business=business, page_type=page_type)
            },
            'hero_heading_size': {
                'model': SubPage,
                'field': 'hero_heading_size',
                'choices': get_font_sizes('heading'),
                'instance': SubPage.objects.get(business=business, page_type=page_type)
            },
            'hero_subheading_size': {
                'model': SubPage,
                'field': 'hero_subheading_size',
                'choices': get_font_sizes('subheading'),
                'instance': SubPage.objects.get(business=business, page_type=page_type)
            },
            'footer_style': {
                'model': business,
                'field': 'footer_style',
                'choices': business.FOOTER_CHOICES,
                'instance': business
            },
            'hero_size': {
                'model': SubPage,
                'field': 'hero_size',
                'choices': SubPage.HERO_SIZE_CHOICES,
                'instance': SubPage.objects.get(business=business, page_type=page_type)
            },
            'is_published': {
                'model': SubPage,
                'field': 'is_published',
                'instance': subpage,
            },
            
        }

        if component not in component_map:
            return JsonResponse({'error': f'Invalid component: {component}'}, status=400)

        component_info = component_map[component]

        if component == 'is_published':
            if isinstance(style, str):
                style = style.lower() == 'true'
            logger.debug(f"Updating publish state for page {page_type} to {style}")
            # Update the instance
            instance = component_info['instance']
            setattr(instance, component_info['field'], style)
            instance.save(update_fields=[component_info['field']])
            
            # Log successful update
            logger.debug(f"Successfully updated publish state for page {page_type} to {style}")
            
            return JsonResponse({'success': True})

        else:
            # Validate choices for all other components
            if component == 'main_font':
                valid_styles = [font[0] for font in component_info['choices']]
            else:
                valid_styles = [choice[0] for choice in component_info['choices']]

            # Only validate non-boolean components
            if style not in valid_styles:
                return JsonResponse({
                    'error': f'Invalid {component} style. Got "{style}", expected one of: {valid_styles}'
                }, status=400)

        # Get the instance to update
        instance = component_info['instance']
        field_name = component_info['field']

        # Update the specific field
        setattr(instance, field_name, style)
        
        # Save only the updated field
        instance.save(update_fields=[field_name])
        
        logger.debug(f"Successfully updated {component} to {style}")
        return JsonResponse({'success': True})

    except SubPage.DoesNotExist:
        logger.error(f"SubPage not found for {page_type}")
        return JsonResponse({'error': f'Page {page_type} not found'}, status=404)
    except Exception as e:
        logger.error(f"Error in update_global_component: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
    
@require_POST
@login_required
def save_layout(request, business_subdirectory):
    """Save layout preferences"""
    business = get_object_or_404(Business, subdirectory=business_subdirectory, owner=request.user)
    
    try:
        data = json.loads(request.body)
        business.navigation_style = data.get('navigation_style')
        business.hero_style = data.get('hero_style')
        business.primary_color = data.get('primary_color')
        business.secondary_color = data.get('secondary_color')
        business.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def upload_hero_image(request, business_subdirectory):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})

    try:
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        if request.user != business.owner:
            return JsonResponse({'success': False, 'error': 'Unauthorized'})

        page_type = request.POST.get('page_type', 'home')
        banner_type = request.POST.get('banner_type', 'primary')
        image_file = request.FILES.get('image')
        if not image_file:
            return JsonResponse({'success': False, 'error': 'No image provided'})

        return_preview = request.POST.get('return_preview') == 'true'

        # validate image file
        if not image_file:
            return JsonResponse({'success': False, 'error': 'No image provided'})

        # Check file size
        if image_file.size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
            return JsonResponse({
                'success': False, 
                'error': f'File size cannot exceed {settings.FILE_UPLOAD_MAX_MEMORY_SIZE // (1024*1024)}MB'
            })

        # Check file extension
        ext = image_file.name.split('.')[-1].lower()
        if ext not in Image.ALLOWED_EXTENSIONS:
            return JsonResponse({
                'success': False,
                'error': f'Unsupported file extension. Allowed types: {", ".join(Image.ALLOWED_EXTENSIONS)}'
            })
        
        try:
            with PILImage.open(image_file) as img:
                img.verify()
                # Reset file pointer after verify
                image_file.seek(0)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Invalid image file'
            })
        logger.debug(f"Processing {banner_type} image upload for {business_subdirectory}, page type: {page_type}")
        logger.debug(f"Image file: {image_file.name}, size: {image_file.size}")

        # Get or create the subpage
        subpage, created = SubPage.objects.get_or_create(
            business=business,
            page_type=page_type,
            defaults={
                'title': f"{business.business_name} {page_type.title()}",
            }
        )

        # Determine the alt_text based on banner type
        alt_text_map = {
            'hero_primary': 'hero_primary',
            'banner_2': 'banner_2',
            'banner_3': 'banner_3',
        }
        alt_text = alt_text_map.get(banner_type)
        
        if not alt_text:
            logger.error(f"Invalid banner type received: {banner_type}")
            return JsonResponse({'error': f'Invalid banner type: {banner_type}'}, status=400)

        # Remove existing image for this banner type if it exists
        content_type = ContentType.objects.get_for_model(SubPage)
        old_image = Image.objects.filter(
            content_type=content_type,
            object_id=subpage.id,
            alt_text=alt_text
        ).first()
        
        if old_image:
            logger.debug(f"Removing old {banner_type} image: {old_image.image.url}")
            old_image.delete()

        # Create new image
        try:
            new_image = Image.objects.create(
                image=image_file,
                uploaded_by=request.user,
                content_type=content_type,
                object_id=subpage.id,
                alt_text=alt_text,
                caption=f'{banner_type.title()} image for {business.business_name} {page_type} page'
            )
        except ValidationError as e:
            logger.error(f"Validation error during image upload: {str(e)}")
            # Convert ValidationError to a more readable format
            if hasattr(e, 'message_dict'):
                error_message = '; '.join([f"{k}: {', '.join(v)}" for k, v in e.message_dict.items()])
            else:
                error_message = str(e)
            return JsonResponse({
                'success': False,
                'error': error_message
            })

        image_url = new_image.image.url
        logger.debug(f"New {banner_type} image created with URL: {image_url}")
        response_data = {
            'success': True,
            'image_url': image_url,
            'debug_info': {
                'subpage_id': subpage.id,
                'content_type': str(content_type),
                'alt_text': new_image.alt_text,
                'banner_type': banner_type
            }
        }
        if return_preview:
            preview_html = render_to_string(f'visitor_pages/{page_type}.html', {
                'business_details': business,
                'subpage': subpage,
                'hero_primary': subpage.get_hero_primary(),
                'banner_2': subpage.get_banner_2(),
                'banner_3': subpage.get_banner_3(),
                'hero_primary': subpage.get_hero_primary(),
                'preview_mode': True,
                'business_subdirectory': business_subdirectory,
                'debug': True,
                'primary_color': business.primary_color,
                'secondary_color': business.secondary_color,
                'text_color': business.text_color,
                'hover_color': business.hover_color,
                'navigation_style': business.navigation_style,
                'footer_style': business.footer_style,
                'is_published': subpage.is_published
            })
            response_data['preview_html'] = preview_html

        return JsonResponse(response_data)

    except Exception as e:
        logger.error(f"Error in upload_hero_image: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def remove_hero_image(request, business_subdirectory):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})

    try:
        # Parse the JSON body
        data = json.loads(request.body)
        print(f"data={data}")
        page_type = data.get('page_type')
        banner_type = data.get('banner_type')  # Add this
        return_preview = data.get('return_preview', False)  # Add this
        
        if not page_type or not banner_type:
            return JsonResponse({'success': False, 'error': 'Page type and banner type required'})

        # Get the business and verify ownership
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        if request.user != business.owner:
            return JsonResponse({'success': False, 'error': 'Unauthorized'})

        # Get the specific subpage
        subpage = get_object_or_404(SubPage, business=business, page_type=page_type)

        # Get and delete the specific banner image
        content_type = ContentType.objects.get_for_model(SubPage)
        print(f"page_type={page_type},banner_type={banner_type}, content_type={content_type}")
        hero_image = Image.objects.filter(
            content_type=content_type,
            object_id=subpage.id,
            alt_text=banner_type  # Use the specific banner type
        ).first()

        response_data = {'success': True}
        print(hero_image)
        if hero_image:
            print(f"Deleting {banner_type} image: {hero_image.id} for subpage: {subpage.id}")
            hero_image.delete()
            response_data['message'] = f'{banner_type} image removed successfully'
        else:
            print(f"No {banner_type} image found for subpage: {subpage.id}")
            response_data['message'] = f'No {banner_type} image found'

        # Add preview HTML if requested
        if return_preview:
            preview_html = render_to_string(f'visitor_pages/{page_type}.html', {
                'business_details': business,
                'subpage': subpage,
                'banner_2': subpage.get_banner_2(),
                'banner_3': subpage.get_banner_3(),
                'hero_primary': subpage.get_hero_primary(),
                'preview_mode': True,
                'business_subdirectory': business_subdirectory,
                'debug': True,
                'primary_color': business.primary_color,
                'secondary_color': business.secondary_color,
                'text_color': business.text_color,
                'hover_color': business.hover_color,
                'navigation_style': business.navigation_style,
                'footer_style': business.footer_style,
                'is_published': subpage.is_published
            })
            response_data['preview_html'] = preview_html

        return JsonResponse(response_data)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    except Exception as e:
        print(f"Error removing hero image: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def update_subpage_hero(request, business_subdirectory, subpage_id):
    try:
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        if request.user != business.owner:
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

        subpage = get_object_or_404(SubPage, id=subpage_id, business=business)
        data = json.loads(request.body)
        
        field = data.get('field')
        value = data.get('value')

        valid_fields = ['heading', 'subheading', 'button_text', 'layout']
        if field not in valid_fields:
            return JsonResponse({'success': False, 'error': 'Invalid field'}, status=400)

        setattr(subpage, f'hero_{field}', value)
        subpage.save()

        return JsonResponse({'success': True})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
# @login_required
# def update_hero(request, business_subdirectory):
#     if request.method != 'POST':
#         return JsonResponse({'success': False, 'error': 'Invalid method'})

#     try:
#         data = json.loads(request.body)
#         field = data.get('field')
#         value = data.get('value', 'default')  # Provide a default value
#         page_type = data.get('page_type')

#         logger.debug(f"Updating hero field: {field} to value: {value} for page: {page_type}")

#         business = get_object_or_404(Business, subdirectory=business_subdirectory)
#         if request.user != business.owner:
#             return JsonResponse({'success': False, 'error': 'Unauthorized'})

#         subpage = get_object_or_404(SubPage, business=business, page_type=page_type)
        
#         # Map of frontend field names to model field names
#         field_mapping = {
#             # hero fields
#             'text_align': 'hero_text_align',
#             'hero_heading': 'hero_heading',
#             'hero_heading_size': 'hero_heading_size',
#             'hero_subheading': 'hero_subheading',
#             'hero_subheading_size': 'hero_subheading_size',
#             'hero_heading_font': 'hero_heading_font',
#             'hero_subheading_font': 'hero_subheading_font',
#             'hero_heading_color': 'hero_heading_color',
#             'hero_subheading_color': 'hero_subheading_color',
#             'show_hero_heading': 'show_hero_heading',
#             'show_hero_subheading': 'show_hero_subheading',
#             'hero_layout': 'hero_layout',
#             'hero_size': 'hero_size',
#             'hero_button_text': 'hero_button_text',
#             # hero button fields
#             'hero_button_link': 'hero_button_link',
#             'show_hero_button': 'show_hero_button',
#             'hero_button_bg_color': 'hero_button_bg_color',
#             'hero_button_text_color': 'hero_button_text_color',
#             'hero_button_size': 'hero_button_size',
#             # Banner 2 fields
#             'hero_banner_2_heading': 'banner_2_heading',
#             'hero_banner_2_subheading': 'banner_2_subheading',
#             'show_hero_banner_2_heading': 'show_banner_2_heading',
#             'show_hero_banner_2_subheading': 'show_banner_2_subheading',
#             'hero_banner_2_heading_font': 'banner_2_heading_font',
#             'hero_banner_2_heading_size': 'banner_2_heading_size',
#             'hero_banner_2_heading_color': 'banner_2_heading_color',
#             'hero_banner_2_subheading_font': 'banner_2_subheading_font',
#             'hero_banner_2_subheading_size': 'banner_2_subheading_size',
#             'hero_banner_2_subheading_color': 'banner_2_subheading_color',
#             'hero_banner_2_text_align': 'banner_2_text_align',
#             # banner 2 button fields
#             'hero_banner_2_button_text': 'banner_2_button_text',
#             'hero_banner_2_button_link': 'banner_2_button_link',
#             'show_hero_banner_2_button': 'show_banner_2_button',
#             'hero_banner_2_button_bg_color': 'banner_2_button_bg_color',
#             'hero_banner_2_button_text_color': 'banner_2_button_text_color',
#             'hero_banner_2_button_size': 'banner_2_button_size',
#             # Banner 3 fields
#             'hero_banner_3_heading': 'banner_3_heading',
#             'hero_banner_3_subheading': 'banner_3_subheading',
#             'show_hero_banner_3_heading': 'show_banner_3_heading',
#             'show_hero_banner_3_subheading': 'show_banner_3_subheading',
#             'hero_banner_3_heading_font': 'banner_3_heading_font',
#             'hero_banner_3_heading_size': 'banner_3_heading_size',
#             'hero_banner_3_heading_color': 'banner_3_heading_color',
#             'hero_banner_3_subheading_font': 'banner_3_subheading_font',
#             'hero_banner_3_subheading_size': 'banner_3_subheading_size',
#             'hero_banner_3_subheading_color': 'banner_3_subheading_color',
#             'hero_banner_3_text_align': 'banner_3_text_align',
#             # banner 3 button fields
#             'hero_banner_3_button_text': 'banner_3_button_text',
#             'hero_banner_3_button_link': 'banner_3_button_link',
#             'show_hero_banner_3_button': 'show_banner_3_button',
#             'hero_banner_3_button_bg_color': 'banner_3_button_bg_color',
#             'hero_banner_3_button_text_color': 'banner_3_button_text_color',
#             'hero_banner_3_button_size': 'banner_3_button_size',
#         }
#         # Get the correct field name from the mapping
#         model_field = field_mapping.get(field)
#         print(f"Field mapping result: {model_field}")
#         logger.debug(f"Field mapping result: {model_field}")
#         logger.debug(f"Current value in database: {getattr(subpage, model_field, None)}")
#         logger.debug(f"New value being set: {value}")
#         if not model_field:
#             return JsonResponse({'success': False, 'error': f'Invalid field: {field}'})

#         # Ensure value is not None before setting
#         if value is not None:
#             setattr(subpage, model_field, value)
#             subpage.save()
#             logger.debug(f"Successfully updated {model_field} to {value}")
#             return JsonResponse({'success': True})
#         else:
#             return JsonResponse({'success': False, 'error': 'Value cannot be null'})

#     except Exception as e:
#         logger.error(f"Error in update_hero: {str(e)}")
#         return JsonResponse({'success': False, 'error': str(e)})
    

@require_POST
def update_hero(request, business_subdirectory):
    # Convert old format to new format
    data = json.loads(request.body)
    new_data = {
        'fieldType': 'text',  # or appropriate type
        'fieldName': data.get('field'),
        'value': data.get('value'),
        'page_type': data.get('page_type')
    }
    request._body = json.dumps(new_data).encode('utf-8')
    return update_layout(request, business_subdirectory)

@login_required
def layout_editor(request, business_subdirectory):
    try:
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        if request.user != business.owner:
            return HttpResponseForbidden()

        # Get current page type from query params or default to 'home'
        current_page = request.GET.get('page_type', 'home')
        # Get available pages for the button links
        published_pages = SubPage.get_published_subpages(business)
        available_pages = [
            page for page in published_pages 
            if page['page_type'] != current_page
        ]

        # Get all subpages for this Business
        subpages = {
            page_type: SubPage.objects.get_or_create(
                business=business,
                page_type=page_type,
                defaults={'title': f"{business.business_name} {page_type.title()}"}
            )[0]
            for page_type in ['home', 'about', 'menu', 'events', 'specials']
        }

        # Get current subpage
        subpage = subpages[current_page]

        context = {
            'business_details': business,
            'business_subdirectory': business_subdirectory,
            'subpages': subpages,
            'subpage': subpage,
            'current_page': current_page,
            'page_type': current_page,    
            'hero_choices': SubPage.HERO_CHOICES,
            'nav_styles': business.NAV_CHOICES,
            'available_pages': available_pages,
        }

        logger.debug(f"Layout editor context: {context}")
        return render(request, 'components/layout_editor/layout_editor.html', context)

    except Exception as e:
        logger.error(f"Error in layout_editor: {str(e)}")
        logger.exception("Full traceback:")
        return HttpResponse(f"Error loading layout editor: {str(e)}", status=500)


@login_required
def page_view(request, business_subdirectory, page_type):
    """View for rendering the actual page content"""
    business = get_object_or_404(Business, subdirectory=business_subdirectory)
    subpage = get_object_or_404(SubPage, business=business, page_type=page_type)
    
    context = {
        'business': business,
        'subpage': subpage,
        'hero_primary': subpage.get_hero_image(),
    }
    
    template_name = f'pages/{page_type}.html'
    return render(request, template_name, context)


@login_required
def page_content(request, business_subdirectory, page_type):
    try:
        logger.debug(f"=== Starting page_content view ===")
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        subpage = get_object_or_404(SubPage, business=business, page_type=page_type)
        
        # Debug the subpage
        logger.debug(f"Found subpage: {subpage.id} with layout: {subpage.hero_layout}")
        
        # Get hero images with detailed logging
        hero_primary = subpage.get_hero_primary()
        logger.debug(f"get_hero_primary() returned: {hero_primary}")
        
        banner_2 = subpage.get_banner_2()
        logger.debug(f"get_banner_2() returned: {banner_2}")
        
        banner_3 = subpage.get_banner_3()
        logger.debug(f"get_banner_3() returned: {banner_3}")
        
        # Create context
        context = {
            'business_details': business,
            'subpage': subpage,
            'hero_primary': hero_primary,
            'banner_2': banner_2,
            'banner_3': banner_3,
            'business_subdirectory': business_subdirectory,
            'is_preview': True,
            'debug': True,
            'page_type': page_type,
        }
        
        # Log the final context
        logger.debug("=== Context being sent to template ===")
        for key, value in context.items():
            logger.debug(f"{key}: {value}")
        
        template_name = f'components/hero/{subpage.hero_layout}.html'
        logger.debug(f"Using template: {template_name}")
        
        response = render(request, template_name, context)
        logger.debug("=== Finished rendering template ===")
        return response
        
    except Exception as e:
        logger.error(f"Error in page_content: {str(e)}")
        logger.exception("Full traceback:")
        return HttpResponse(f"Error loading page content: {str(e)}", status=500)
    
@login_required
def update_brand_colors(request, business_subdirectory):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})

    try:
        data = json.loads(request.body)
        color_type = data.get('color_type')
        color_value = data.get('color_value')

        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        if request.user != business.owner:
            return JsonResponse({'success': False, 'error': 'Unauthorized'})

        # Update the appropriate color field
        if color_type == 'primary':
            business.primary_color = color_value
        elif color_type == 'secondary':
            business.secondary_color = color_value
        elif color_type == 'hover-color':
            business.hover_color = color_value
        elif color_type == 'text-color':
            business.text_color = color_value
        else:
            return JsonResponse({'success': False, 'error': 'Invalid color type'})

        business.save()
        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})