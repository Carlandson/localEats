from django.apps import apps
from django.contrib.contenttypes.models import ContentType
import requests
from django.conf import settings
from typing import Dict, Any, List
from urllib.parse import urlencode

import logging

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

    def __init__(self, api_key=None):
        self.api_key = api_key or settings.PRINTFUL_SECRET_KEY
        logger.debug(f"PrintfulClient initialized with API key: {api_key[:5]}..." if api_key else "default key")

    def get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    @classmethod
    def get_oauth_url(cls, state: str) -> str:
        """Generate OAuth URL for Printful authorization"""
        logger.info(f"PRINTFUL_CLIENT_ID: {settings.PRINTFUL_CLIENT_ID}")
        logger.info(f"PRINTFUL_REDIRECT_URL: {settings.PRINTFUL_REDIRECT_URL}")
        
        params = {
            'client_id': settings.PRINTFUL_CLIENT_ID,
            'redirect_url': settings.PRINTFUL_REDIRECT_URL.rstrip('/'),
            'response_type': 'code',
            'state': state,
            'scope': 'sync_products sync_products/read file_library product_templates'  # Updated scopes
        }
        query_string = urlencode(params)
        oauth_url = f"{cls.OAUTH_URL}?{query_string}"
        
        logger.info(f"Generated OAuth URL: {oauth_url}")
        return oauth_url

    @classmethod
    def exchange_code_for_token(cls, code: str, redirect_url: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        logger.debug("Exchanging code for token")
        try:
            response = requests.post(
                cls.TOKEN_URL,
                data={
                    'grant_type': 'authorization_code',
                    'code': code,
                    'client_id': settings.PRINTFUL_CLIENT_ID,
                    'client_secret': settings.PRINTFUL_SECRET_KEY,
                    'redirect_url': redirect_url
                }
            )
            response.raise_for_status()
            token_data = response.json()
            logger.debug("Successfully exchanged code for token")
            return token_data
        except Exception as e:
            logger.error(f"Error exchanging code for token: {str(e)}")
            raise

    def update_store(self, store_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update store information"""
        logger.debug(f"Attempting to update store with data: {store_data}")
        try:
            response = requests.put(
                f"{self.BASE_URL}/store",
                headers=self.get_headers(),
                json=store_data
            )
            logger.debug(f"Store update response status: {response.status_code}")
            logger.debug(f"Store update response body: {response.text}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to update store: {str(e)}")
            if hasattr(e, 'response'):
                logger.error(f"Error response: {e.response.text}")
            raise