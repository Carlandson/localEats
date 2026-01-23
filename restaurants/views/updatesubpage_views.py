# Django core imports
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
import json

# Local imports
from ..models import (SubPage, 
    Business, HomePage, ContactPage, AboutUsPage, 
    ProductsPage, ServicesPage, GalleryPage,
    Event, SpecialsPage, NewsFeed, NewsPost, Comment, ContactMessage
)

@login_required
@require_http_methods(["POST"])
def update_page_settings(request, business_subdirectory):
    try:
        data = json.loads(request.body)
        subpage_type = data.get('page_type')
        subpage = SubPage.objects.get(business__subdirectory=business_subdirectory, page_type=subpage_type)
        PageModel = apps.get_model('restaurants', subpage_type)
        page_object, created = PageModel.objects.get_or_create(subpage=subpage)
        field_name = data.get('fieldName')
        if not hasattr(page_object, field_name):
            return JsonResponse({'status': 'error', 'message': 'Invalid field name'}, status=400)
        value = data.get(field_name, getattr(page_object, field_name))
        setattr(page_object, field_name, value)
        page_object.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Setting updated successfully',
            'field': field_name,
            'value': value
        })

    except SubPage.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Subpage not found'
        }, status=404)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def update_contact_page_settings(request, business_subdirectory):
    # request contains subpage type
    try:
        data = json.loads(request.body)
        subpage = SubPage.objects.get(
            business__subdirectory=business_subdirectory,
            business__owner=request.user,  # Ensure owner
            page_type='contact'
        )
        contact_page, created = ContactPage.objects.get_or_create(subpage=subpage)

        # Handle content updates
        if data.get('fieldName') == 'description':
            contact_page.description = data.get('description', contact_page.description)
            contact_page.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Description updated successfully',
                'description': contact_page.description
            })

        # Handle boolean toggle updates
        field_name = data.get('fieldName')
        new_value = data.get('value')
        
        allowed_fields = [
            'show_description',
            'show_map',
            'show_contact_form',
            'description'
        ]
        
        if field_name not in allowed_fields:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid field name'
            }, status=400)
        
        setattr(contact_page, field_name, new_value)
        contact_page.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Setting updated successfully',
            'field': field_name,
            'value': new_value
        })

    except SubPage.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Contact page not found'
        }, status=404)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
    

@login_required
@require_http_methods(["POST"])
def update_about_page_settings(request, business_subdirectory):
    try:
        data = json.loads(request.body)
        subpage = SubPage.objects.get(business__subdirectory=business_subdirectory, page_type='about')
        about_page, created = AboutUsPage.objects.get_or_create(subpage=subpage)
        print(data.get('fieldName'))
        # Handle content section updates
        if data.get('fieldName') in ['content', 'history', 'team_members', 'mission_statement', 'core_values']:
            field_name = data.get('fieldName')
            print(field_name)
            setattr(about_page, field_name, data.get(field_name, getattr(about_page, field_name)))
            about_page.save()
            return JsonResponse({
                'status': 'success',
                'message': f'{field_name.replace("_", " ").title()} updated successfully',
                field_name: getattr(about_page, field_name)
            })

        # Handle boolean toggle updates
        field_name = data.get('fieldName')
        new_value = data.get('value')
        
        allowed_fields = [
            'show_history',
            'show_team',
            'show_mission',
            'show_values',
            'team_members',
            'core_values',
            'mission_statement',
            'history'
        ]
        
        if field_name not in allowed_fields:
            print(data.get('fieldName'))
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid field name'
            }, status=400)
        
        setattr(about_page, field_name, new_value)
        about_page.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Setting updated successfully',
            'field': field_name,
            'value': new_value
        })

    except SubPage.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Subpage not found'
        }, status=404)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
    

@login_required
@require_POST
def update_products_page_settings(request, business_subdirectory):
    try:
        business = Business.objects.get(subdirectory=business_subdirectory)
        subpage = SubPage.objects.get(business=business, page_type='products')
        products_page = getattr(subpage, 'products_content', None)
        
        if not products_page:
            return JsonResponse({'error': 'Products page not found'}, status=404)

        data = json.loads(request.body)
        field_name = data.get('fieldName')
        
        if field_name == 'description':
            products_page.description = data.get('description', '')
            products_page.save()
        elif field_name == 'show_description':
            products_page.show_description = data.get('value', False)
            products_page.save()
        else:
            return JsonResponse({'error': 'Invalid field name'}, status=400)
            
        return JsonResponse({'status': 'success'})
        
    except (Business.DoesNotExist, SubPage.DoesNotExist, json.JSONDecodeError) as e:
        return JsonResponse({'error': str(e)}, status=400)
    

@login_required
def update_services_page_settings(request, business_subdirectory):
    try:
        business = Business.objects.get(subdirectory=business_subdirectory)
        subpage = SubPage.objects.get(business=business, page_type='services')
        services_page = getattr(subpage, 'services_content', None)
        
        if not services_page:
            return JsonResponse({'error': 'Services page not found'}, status=404)

        data = json.loads(request.body)
        field_name = data.get('fieldName')
        
        if field_name == 'description':
            services_page.description = data.get('description', '')
            services_page.save()
        elif field_name == 'show_description':
            services_page.show_description = data.get('value', False)
            services_page.save()
        else:
            return JsonResponse({'error': 'Invalid field name'}, status=400)
            
        return JsonResponse({'status': 'success'})
        
    except (Business.DoesNotExist, SubPage.DoesNotExist, json.JSONDecodeError) as e:
        return JsonResponse({'error': str(e)}, status=400)
    

@login_required
def update_gallery_page_settings(request, business_subdirectory):
    try:
        business = Business.objects.get(subdirectory=business_subdirectory)
        subpage = SubPage.objects.get(business=business, page_type='gallery')
        gallery_page = getattr(subpage, 'gallery_content', None)
        
        if not gallery_page:
            return JsonResponse({'error': 'Gallery page not found'}, status=404)

        data = json.loads(request.body)
        field_name = data.get('fieldName')
        
        if field_name == 'description':
            gallery_page.description = data.get('description', '')
            gallery_page.save()
        elif field_name == 'show_description':
            gallery_page.show_description = data.get('value', False)
            gallery_page.save()
        else:
            return JsonResponse({'error': 'Invalid field name'}, status=400)
            
        return JsonResponse({'status': 'success'})
        
    except (Business.DoesNotExist, SubPage.DoesNotExist, json.JSONDecodeError) as e:
        return JsonResponse({'error': str(e)}, status=400)
    
@login_required
@require_http_methods(["POST"])
def update_home_page_settings(request, business_subdirectory):
    print(business_subdirectory)
    try:
        data = json.loads(request.body)
        subpage = SubPage.objects.get(business__subdirectory=business_subdirectory, page_type='home')
        print(subpage)
        home_page, created = HomePage.objects.get_or_create(subpage=subpage)

        # Handle welcome section update
        if data.get('fieldName') == 'show_welcome' and ('welcome_title' in data or 'welcome_message' in data):
            home_page.welcome_title = data.get('welcome_title', home_page.welcome_title)
            home_page.welcome_message = data.get('welcome_message', home_page.welcome_message)
            home_page.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Welcome content updated successfully',
                'welcome_title': home_page.welcome_title,
                'welcome_message': home_page.welcome_message
            })

        # Handle boolean toggle updates
        field_name = data.get('fieldName')
        new_value = data.get('value')
        
        allowed_fields = [
            'show_welcome',
            'show_daily_special',
            'show_affiliates',
            'show_newsfeed',
            'show_upcoming_event',
            'show_featured_service',
            'show_featured_product'
        ]
        
        if field_name not in allowed_fields:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid field name'
            }, status=400)
        
        setattr(home_page, field_name, new_value)
        home_page.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Setting updated successfully',
            'field': field_name,
            'value': new_value
        })

    except SubPage.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Subpage not found'
        }, status=404)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)