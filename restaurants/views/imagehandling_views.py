import logging
import json
from django.conf import settings
# Django core imports
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.views.decorators.http import require_http_methods
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
import base64
import logging

# Third-party imports
from PIL import Image as PILImage

# Local imports
from ..models import Business, SubPage, Image

logger = logging.getLogger(__name__)

@login_required
@require_POST
def upload_hero_image(request, business_subdirectory):
    print("upload_hero_image called")
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
    print("remove_hero_image called")
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
@require_POST
def upload_gallery_image(request, business_subdirectory):
    try:
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        if request.user != business.owner:
            return JsonResponse({"error": "Unauthorized"}, status=403)

        subpage = get_object_or_404(SubPage, business=business, page_type='gallery')
        gallery_page = getattr(subpage, 'gallery_content', None)
        
        if not gallery_page:
            gallery_page = GalleryPage.objects.create(subpage=subpage)

        file = request.FILES.get('image')  # Changed from getlist to get

        if not file:
            return JsonResponse({"error": "No image provided"}, status=400)

        # Create and save single image
        image = Image(
            image=file,
            uploaded_by=request.user,
            content_type=ContentType.objects.get_for_model(gallery_page),
            object_id=gallery_page.id,
            alt_text=file.name
        )
        image.full_clean()  # This will validate the image
        image.save()

        return JsonResponse({
            "success": True,
            "message": "Successfully uploaded image",
            "image": {  # Changed from images to image
                'id': image.id,
                'url': image.image.url,
                'thumbnail_url': image.thumbnail.url if image.thumbnail else None,
            }
        })

    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        logger.error(f"Error uploading gallery image: {str(e)}")
        return JsonResponse({"error": "Server error"}, status=500)


@login_required
@require_http_methods(['DELETE'])
def delete_gallery_image(request, business_subdirectory, image_id):
    try:
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        if request.user != business.owner:
            return JsonResponse({"error": "Unauthorized"}, status=403)

        subpage = get_object_or_404(SubPage, business=business, page_type='gallery')
        gallery_page = getattr(subpage, 'gallery_content', None)
        
        if not gallery_page:
            return JsonResponse({"error": "Gallery page not found"}, status=404)

        image = get_object_or_404(Image, id=image_id, content_type=ContentType.objects.get_for_model(gallery_page), object_id=gallery_page.id)
        
        # Delete the image file and record
        image.image.delete(save=False)
        image.thumbnail.delete(save=False)
        image.delete()

        return JsonResponse({"success": True})

    except Exception as e:
        logger.error(f"Error deleting gallery image: {str(e)}")
        return JsonResponse({"error": "Server error"}, status=500)