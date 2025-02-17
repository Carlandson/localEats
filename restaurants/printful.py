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
            'scope': 'all'
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