import requests

class PrintfulClient:
    BASE_URL = 'https://api.printful.com'
    
    def __init__(self, api_key):
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def create_product(self, product_data):
        return requests.post(
            f'{self.BASE_URL}/store/products',
            headers=self.headers,
            json=product_data
        ).json()