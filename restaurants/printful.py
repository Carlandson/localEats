import requests
from django.conf import settings
from urllib.parse import urlencode
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class PrintfulClient:
    BASE_URL = 'https://api.printful.com'
    OAUTH_URL = 'https://www.printful.com/oauth/authorize'
    TOKEN_URL = 'https://www.printful.com/oauth/token'

    @classmethod
    def get_oauth_url(cls, state: str) -> str:
        """Generate OAuth URL for Printful authorization"""
        # Add debug logging
        logger.info(f"PRINTFUL_CLIENT_ID: {settings.PRINTFUL_CLIENT_ID}")
        logger.info(f"PRINTFUL_REDIRECT_URI: {settings.PRINTFUL_REDIRECT_URI}")
        
        params = {
            'client_id': settings.PRINTFUL_CLIENT_ID,
            'redirect_uri': settings.PRINTFUL_REDIRECT_URI.rstrip('/'),  # Ensure no trailing slash
            'response_type': 'code',
            'state': state,
            'scope': 'all'
        }
        query_string = urlencode(params)
        oauth_url = f"{cls.OAUTH_URL}?{query_string}"
        
        # Log the final URL
        logger.info(f"Generated OAuth URL: {oauth_url}")
        return oauth_url