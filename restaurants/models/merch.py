from django.db import models


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

    class Meta:
        indexes = [
            models.Index(fields=['provider_product_id']),
            models.Index(fields=['business', 'is_active']),
        ]