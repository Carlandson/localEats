# Django core imports
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
import logging

# Local imports
from ..models import Business, SubPage

logger = logging.getLogger(__name__)

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
    
def update_global_component(request, business_subdirectory):
    print("update_global_component called")
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