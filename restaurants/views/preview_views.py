# Django core imports
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.template.loader import render_to_string
import logging

# Local imports
from ..models import Business

logger = logging.getLogger(__name__)

@login_required
def preview_navigation(request, business_subdirectory, style):
    print("preview_navigation called")
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
    
@login_required
def preview_component(request, business_subdirectory):
    print("preview_component called")
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
def preview_page(request, business_subdirectory, page_type):
    print("preview_page called")
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
            'hero_banner_2': banner_2,  # Alias for template compatibility
            'hero_banner_3': banner_3,  # Alias for template compatibility
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