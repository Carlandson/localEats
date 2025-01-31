from django.apps import apps
from django.contrib.contenttypes.models import ContentType
import requests
from django.conf import settings
from typing import Dict, Any, List
import json
import logging
from django.utils import timezone
from .models import PODAccount, PODProduct
from urllib.parse import urlencode
logger = logging.getLogger(__name__)

def get_business_images(business):
    """Get all images associated with a business's products, services, and events"""
    
    # Get models using apps.get_model to avoid circular imports
    Product = apps.get_model('restaurants', 'Product')
    Service = apps.get_model('restaurants', 'Service')
    Event = apps.get_model('restaurants', 'Event')
    Image = apps.get_model('restaurants', 'Image')
    SubPage = apps.get_model('restaurants', 'SubPage')
    
    images_data = []
    
    try:
        # Get all relevant subpages in one query
        subpages = SubPage.objects.filter(
            business=business
        ).select_related(
            'products_content',
            'services_content',
            'events_content'
        )

        # Get products page and its images
        products_page = next((sp.products_content for sp in subpages if hasattr(sp, 'products_content')), None)
        if products_page:
            products = Product.objects.filter(business=business)
            for product in products:
                product_images = Image.objects.filter(
                    content_type=ContentType.objects.get_for_model(Product),
                    object_id=product.id
                ).select_related('uploaded_by')
                
                for image in product_images:
                    images_data.append({
                        'id': image.id,
                        'url': image.image.url,
                        'thumbnail_url': image.thumbnail.url if image.thumbnail else None,
                        'alt_text': image.alt_text,
                        'caption': image.caption,
                        'upload_date': image.upload_date,
                        'uploaded_by': image.uploaded_by.get_full_name() or image.uploaded_by.username,
                        'content_type': 'Product',
                        'content_name': product.name,
                        'content_url': f'/products/{product.id}/'
                    })

        # Get services page and its images
        services_page = next((sp.services_content for sp in subpages if hasattr(sp, 'services_content')), None)
        if services_page:
            services = Service.objects.filter(business=business)
            for service in services:
                service_images = Image.objects.filter(
                    content_type=ContentType.objects.get_for_model(Service),
                    object_id=service.id
                ).select_related('uploaded_by')
                
                for image in service_images:
                    images_data.append({
                        'id': image.id,
                        'url': image.image.url,
                        'thumbnail_url': image.thumbnail.url if image.thumbnail else None,
                        'alt_text': image.alt_text,
                        'caption': image.caption,
                        'upload_date': image.upload_date,
                        'uploaded_by': image.uploaded_by.get_full_name() or image.uploaded_by.username,
                        'content_type': 'Service',
                        'content_name': service.name,
                        'content_url': f'/services/{service.id}/'
                    })

        # Get events page and its images
        events_page = next((sp.events_content for sp in subpages if hasattr(sp, 'events_content')), None)
        if events_page:
            events = Event.objects.filter(events_page=events_page)
            for event in events:
                event_images = Image.objects.filter(
                    content_type=ContentType.objects.get_for_model(Event),
                    object_id=event.id
                ).select_related('uploaded_by')
                
                for image in event_images:
                    images_data.append({
                        'id': image.id,
                        'url': image.image.url,
                        'thumbnail_url': image.thumbnail.url if image.thumbnail else None,
                        'alt_text': image.alt_text,
                        'caption': image.caption,
                        'upload_date': image.upload_date,
                        'uploaded_by': image.uploaded_by.get_full_name() or image.uploaded_by.username,
                        'content_type': 'Event',
                        'content_name': event.title,
                        'content_url': f'/events/{event.id}/'
                    })

    except Exception as e:
        logger.error(f"Error fetching images for business {business.id}: {str(e)}")
        
    # Sort all images by upload date
    images_data.sort(key=lambda x: x['upload_date'], reverse=True)
    
    return images_data

class PrintfulClient:
    BASE_URL = 'https://api.printful.com'
    OAUTH_URL = 'https://www.printful.com/oauth/authorize'
    TOKEN_URL = 'https://www.printful.com/oauth/token'

    @classmethod
    def get_oauth_url(cls, state: str, redirect_uri: str) -> str:
        """Generate OAuth URL for Printful authorization"""
        params = {
            'client_id': settings.PRINTFUL_CLIENT_ID,
            'redirect_uri': redirect_uri,  # Use the formatted redirect URI
            'response_type': 'code',
            'state': state,
            'scope': 'all'
        }
        query_string = urlencode(params)
        return f"{cls.OAUTH_URL}?{query_string}"

    @classmethod
    def exchange_code_for_token(cls, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        try:
            response = requests.post(
                cls.TOKEN_URL,
                data={
                    'grant_type': 'authorization_code',
                    'client_id': settings.PRINTFUL_CLIENT_ID,
                    'client_secret': settings.PRINTFUL_SECRET_KEY,
                    'code': code,
                    'redirect_uri': redirect_uri
                }
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error exchanging code for token: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response content: {e.response.text}")
            raise