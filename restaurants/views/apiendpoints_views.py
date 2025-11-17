# Standard library
import json
import logging

# Django core
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.utils import timezone

# Google API
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google_auth_httplib2
import httplib2

# Allauth
from allauth.socialaccount.models import SocialAccount

# Local imports
from ..models import Business, SubPage, Menu, AboutUsPage, EventsPage, SpecialsPage
from ..forms import CustomSignupView
from django.contrib.auth import get_user_model


logger = logging.getLogger(__name__)

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

@require_POST
def update_layout(request, business_subdirectory):
    print("update_layout called")
    try:
        data = json.loads(request.body)
        print("Received data:", data)
        
        field_type = data.get('fieldType')
        field_name = data.get('fieldName', '')
        value = data.get('value', '')
        page_type = data.get('page_type')
        is_global = data.get('isGlobal', False)
        return_preview = data.get('return_preview', False)
        print(f"Parsed values: field_type={field_type}, field_name={field_name}, value={value}, page_type={page_type}")

        # Get the business and subpage
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        response_data = {'success': True}
        # Handle new page creation
        if field_type == 'new_page':
            timestamp = timezone.now().strftime('%Y%m%d-%H%M%S')
            unique_slug = f"{business.subdirectory}-{page_type}-{timestamp}"
            page_type_display = dict(SubPage.PAGE_TYPES).get(page_type, page_type.title())
            # Create the subpage
            new_subpage = SubPage.objects.create(
                business=business,
                page_type=page_type,
                title=f"{business.business_name} {page_type_display}",
                slug=unique_slug,
                is_published=False
            )
            # Create the corresponding page content based on type
            if page_type == 'menu':
                # Create menu and link it to the menu page
                Menu.objects.create(
                    business=business,
                    name=f"{business.business_name} Menu",
                    description="Our main menu",
                    subpage=new_subpage,  # Link menu to the menu page
                    display_style='grid'
                )
            elif page_type == 'about':
                AboutUsPage.objects.create(
                    subpage=new_subpage,
                    content=""
                )
            elif page_type == 'events':
                EventsPage.objects.create(
                    subpage=new_subpage
                )
            elif page_type == 'specials':
                SpecialsPage.objects.create(
                    subpage=new_subpage
                )
            subpage = get_object_or_404(SubPage, business=business, page_type=page_type)
            response_data['message'] = f'Created new {page_type} page'

        # Handle brand color updates
        else:
            subpage = get_object_or_404(SubPage, business=business, page_type=page_type)
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