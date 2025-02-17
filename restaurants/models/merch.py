from django.db import models
import requests
import logging

logger = logging.getLogger(__name__)

"""
Printful
1. Create developer account
2. Create API key
3. Create POD account
4. Create POD product
"""
class PODAccount(models.Model):
    business = models.OneToOneField('Business', on_delete=models.CASCADE)
    provider = models.CharField(max_length=50, choices=[
        ('PRINTFUL', 'Printful'),
        ('PRINTIFY', 'Printify'),
    ])
    api_key = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['provider']),
        ]

class PODProduct(models.Model):
    business = models.ForeignKey('Business', on_delete=models.CASCADE)
    pod_account = models.ForeignKey(PODAccount, on_delete=models.CASCADE)
    provider_product_id = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    design_data = models.JSONField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def update_store(self, store_data):
        """Update store information"""
        try:
            response = requests.put(
                f'{self.API_URL}/store',
                headers=self.get_headers(),
                json=store_data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update store: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Printful API response: {e.response.text}")
            raise
    class Meta:
        indexes = [
            models.Index(fields=['provider_product_id']),
            models.Index(fields=['business', 'is_active']),
        ]