"""
Reusable utilities for upload operations.
Provides rate limiting and storage quota checks that can be used across different upload types.
"""
import logging
from typing import Tuple, Optional
from django.core.cache import cache
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum, Q

from ..models import Business, Image, GalleryPage

logger = logging.getLogger(__name__)

# Constants
MAX_STORAGE_PER_BUSINESS = 500 * 1024 * 1024  # 500MB
MAX_UPLOADS_PER_HOUR = 50
MAX_IMAGES_PER_GALLERY = 100

def check_rate_limit(user, action_type: str = 'upload', max_actions: int = None, 
                     time_window: int = 3600) -> Tuple[bool, Optional[JsonResponse]]:
    """
    Check if user has exceeded rate limit for a given action.
    
    Args:
        user: Django User object
        action_type: Type of action (e.g., 'upload', 'api_call', 'email_send')
        max_actions: Maximum number of actions allowed (default: MAX_UPLOADS_PER_HOUR)
        time_window: Time window in seconds (default: 3600 = 1 hour)
        
    Returns:
        Tuple of (is_allowed, error_response)
        - is_allowed: True if under limit, False if exceeded
        - error_response: JsonResponse with error if exceeded, None otherwise
    """
    max_actions = max_actions or MAX_UPLOADS_PER_HOUR
    cache_key = f'rate_limit_{action_type}_{user.id}'
    action_count = cache.get(cache_key, 0)
    
    if action_count >= max_actions:
        return False, JsonResponse({
            "error": f"Rate limit exceeded. Maximum {max_actions} {action_type}(s) per {time_window // 60} minutes."
        }, status=429)
    
    # Increment counter
    cache.set(cache_key, action_count + 1, time_window)
    return True, None


def check_storage_quota(business: Business, additional_size: int = 0, 
                       content_type: Optional[ContentType] = None,
                       max_storage: int = None) -> Tuple[bool, int, int, Optional[JsonResponse]]:
    """
    Check if business has exceeded storage quota.
    
    Can be used for different content types (gallery images, documents, videos, etc.)
    
    Args:
        business: Business object
        additional_size: Size of file being uploaded (in bytes)
        content_type: Optional ContentType to filter by (default: GalleryPage)
        max_storage: Maximum storage allowed (default: MAX_STORAGE_PER_BUSINESS)
        
    Returns:
        Tuple of (is_under_quota, current_size, max_size, error_response)
        - is_under_quota: True if under quota, False if exceeded
        - current_size: Current storage used in bytes
        - max_size: Maximum allowed storage in bytes
        - error_response: JsonResponse with error if exceeded, None otherwise
    """
    max_storage = max_storage or MAX_STORAGE_PER_BUSINESS
    
    # Default to GalleryPage if no content_type specified
    if content_type is None:
        gallery_pages = GalleryPage.objects.filter(subpage__business=business)
        if not gallery_pages.exists():
            current_size = 0
        else:
            gallery_content_type = ContentType.objects.get_for_model(GalleryPage)
            current_size = Image.objects.filter(
                content_type=gallery_content_type,
                object_id__in=gallery_pages.values_list('id', flat=True)
            ).aggregate(total=Sum('image__size'))['total'] or 0
    else:
        # Calculate storage for specific content type
        current_size = Image.objects.filter(
            content_type=content_type,
            object_id__in=business.get_related_object_ids(content_type)  # You'd need to implement this
        ).aggregate(total=Sum('image__size'))['total'] or 0
    
    # Check if adding new file would exceed quota
    if current_size + additional_size >= max_storage:
        return False, current_size, max_storage, JsonResponse({
            "error": f"Storage quota exceeded. Current: {current_size / (1024*1024):.1f}MB / Max: {max_storage / (1024*1024):.1f}MB"
        }, status=413)
    
    return True, current_size, max_storage, None

def check_gallery_image_limit(business: Business, max_images: int = None) -> Tuple[bool, int, int, Optional[JsonResponse]]:
    """
    Check if business gallery has exceeded image count limit.
    
    Args:
        business: Business object
        max_images: Maximum number of images allowed (default: MAX_IMAGES_PER_GALLERY)
        
    Returns:
        Tuple of (is_under_limit, current_count, max_images, error_response)
        - is_under_limit: True if under limit, False if exceeded
        - current_count: Current number of images in gallery
        - max_images: Maximum allowed images
        - error_response: JsonResponse with error if exceeded, None otherwise
    """
    max_images = max_images or MAX_IMAGES_PER_GALLERY
    
    # Get all gallery pages for this business
    gallery_pages = GalleryPage.objects.filter(subpage__business=business)
    
    if not gallery_pages.exists():
        current_count = 0
    else:
        gallery_content_type = ContentType.objects.get_for_model(GalleryPage)
        current_count = Image.objects.filter(
            content_type=gallery_content_type,
            object_id__in=gallery_pages.values_list('id', flat=True)
        ).count()
    
    # Check if adding new image would exceed limit
    if current_count >= max_images:
        return False, current_count, max_images, JsonResponse({
            "error": f"Image limit exceeded. Current: {current_count} / Max: {max_images} images."
        }, status=413)
    
    return True, current_count, max_images, None
    
def check_gallery_storage_quota(business: Business, additional_size: int = 0) -> Tuple[bool, int, int, Optional[JsonResponse]]:
    """
    Convenience wrapper for checking gallery storage quota.
    
    Args:
        business: Business object
        additional_size: Size of file being uploaded (in bytes)
        
    Returns:
        Tuple of (is_under_quota, current_size, max_size, error_response)
    """
    gallery_content_type = ContentType.objects.get_for_model(GalleryPage)
    return check_storage_quota(business, additional_size, gallery_content_type)