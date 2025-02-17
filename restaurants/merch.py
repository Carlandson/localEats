from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import PODAccount, PODProduct, Business
from .utils import PrintfulClient
from decimal import Decimal
import secrets
from django.core.cache import cache
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
import logging
from django.conf import settings
from urllib.parse import quote

logger = logging.getLogger(__name__)



@login_required
def merch_dashboard(request, business_subdirectory):
    """Display the merch dashboard for a business."""
    business = get_object_or_404(Business, subdirectory=business_subdirectory)
    if request.user != business.owner:
        raise PermissionDenied
    
    # Get the POD account for this business
    try:
        pod_account = PODAccount.objects.get(business=business)
    except PODAccount.DoesNotExist:
        pod_account = None
    
    # Get products if there's a POD account
    products = []
    if pod_account:
        # Your product fetching logic here
        pass
    
    context = {
        'business_details': business,
        'pod_account': pod_account,  # Make sure this is being passed
        'products': products,
    }
    
    return render(request, 'subpages/merch.html', context)


@login_required
def setup_pod_account(request):
    if request.method == 'POST':
        business = request.user.business
        provider = request.POST.get('provider')
        api_key = request.POST.get('api_key')

        # Check if account already exists
        if PODAccount.objects.filter(business=business).exists():
            messages.error(request, 'POD account already exists')
            return redirect('merch_dashboard')

        try:
            # Validate API key with Printful
            client = PrintfulClient(api_key)
            if not client.validate_api_key():
                messages.error(request, 'Invalid API key')
                return redirect('merch_dashboard')

            PODAccount.objects.create(
                business=business,
                provider=provider,
                api_key=api_key
            )
            messages.success(request, f'Successfully connected to {provider}')
        except Exception as e:
            messages.error(request, f'Error connecting to {provider}: {str(e)}')

    return redirect('merch_dashboard')

@login_required
def get_product_templates(request):
    """API endpoint to get available product templates"""
    try:
        pod_account = PODAccount.objects.get(business=request.user.business)
        client = PrintfulClient(pod_account.api_key)
        templates = client.get_product_templates()
        return JsonResponse({'templates': templates})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def create_product(request):
    if request.method == 'POST':
        business = request.user.business
        pod_account = get_object_or_404(PODAccount, business=business)
        client = PrintfulClient(pod_account.api_key)

        try:
            # Get form data
            title = request.POST.get('title')
            price = Decimal(request.POST.get('price'))
            product_template_id = int(request.POST.get('template_id'))
            design_file = request.FILES.get('design_file')

            # Create design task for mockup generation
            design_task = client.create_design_task({
                'product_id': product_template_id,
                'files': [
                    {
                        'placement': 'front',
                        'image_url': design_file.temporary_file_path(),
                        'position': {
                            'area_width': 1800,
                            'area_height': 2400,
                            'width': 1800,
                            'height': 1800,
                            'top': 300,
                            'left': 0
                        }
                    }
                ]
            })

            # Wait for mockup generation
            mockup_result = client.get_mockup_task_result(design_task['task_key'])

            # Get variants for the product
            variants = client.get_variants(product_template_id)
            
            # Create synchronized product in Printful
            printful_product = client.create_sync_product(
                title=title,
                product_template_id=product_template_id,
                variants=[{
                    'variant_id': variant['id'],
                    'retail_price': str(price)
                } for variant in variants],
                design_files={
                    'thumbnail': mockup_result['mockups'][0]['thumbnail_url'],
                    'preview': mockup_result['mockups'][0]['preview_url']
                }
            )

            # Save product in our database
            product = PODProduct.objects.create(
                business=business,
                pod_account=pod_account,
                provider_product_id=printful_product['id'],
                title=title,
                price=price,
                design_data={
                    'product_type': printful_product['type'],
                    'preview_url': mockup_result['mockups'][0]['preview_url'],
                    'variants': variants,
                    'mockups': mockup_result['mockups']
                }
            )
            messages.success(request, 'Product created successfully')
        except Exception as e:
            messages.error(request, f'Error creating product: {str(e)}')

    return redirect('merch_dashboard')

@login_required
def disconnect_pod_account(request):
    if request.method == 'POST':
        business = request.user.business
        try:
            pod_account = PODAccount.objects.get(business=business)
            
            # Optionally, deactivate all products before disconnecting
            PODProduct.objects.filter(business=business).update(is_active=False)
            
            # Delete the POD account
            pod_account.delete()
            messages.success(request, 'Successfully disconnected Print-on-Demand account')
            
        except PODAccount.DoesNotExist:
            messages.error(request, 'No Print-on-Demand account found')
        except Exception as e:
            messages.error(request, f'Error disconnecting account: {str(e)}')
    
    return redirect('merch_dashboard')

@login_required
def toggle_product(request, product_id):
    """Toggle a product's active status (enable/disable)"""
    if request.method == 'POST':
        business = request.user.business
        product = get_object_or_404(PODProduct, id=product_id, business=business)
        
        try:
            # Toggle the active status
            product.is_active = not product.is_active
            product.save()
            
            # Get the client and sync with Printful
            pod_account = product.pod_account
            client = PrintfulClient(pod_account.api_key)
            
            # Update the product status in Printful
            client._make_request(
                'PUT',
                f'/store/products/{product.provider_product_id}',
                {'sync_product': {'is_ignored': not product.is_active}}
            )
            
            status = 'activated' if product.is_active else 'deactivated'
            messages.success(request, f'Product successfully {status}')
        except Exception as e:
            messages.error(request, f'Error toggling product: {str(e)}')
            
    return redirect('merch_dashboard')


@login_required
@csrf_exempt
def connect_printful(request, business_subdirectory):
    """Start the Printful OAuth flow"""
    logger.info(f"Starting Printful OAuth flow for business: {business_subdirectory}")
    
    business = get_object_or_404(Business, subdirectory=business_subdirectory)
    if request.user != business.owner:
        raise PermissionDenied
    
    # Store business info in session for the callback
    request.session['printful_business'] = business_subdirectory
    
    # Generate state token
    state = secrets.token_urlsafe(32)
    cache.set(f'printful_oauth_state_{state}', {
        'user_id': request.user.id,
        'business_subdirectory': business_subdirectory
    }, timeout=3600)
    
    # Use settings REDIRECT_URL and format with business subdirectory
    redirect_url = settings.PRINTFUL_REDIRECT_URL.format(
        business_subdirectory=business_subdirectory
    )
    
    # Build the OAuth URL with correct parameter name
    oauth_url = (
        f'https://www.printful.com/oauth/authorize'
        f'?client_id={settings.PRINTFUL_CLIENT_ID}'
        f'&redirect_url={quote(redirect_url)}'
        f'&response_type=code'
        f'&state={state}'
        f'&scope={quote("sync_products sync_products/read file_library product_templates")}'  # Updated scopes
    )
    
    logger.info(f"Redirecting to Printful OAuth URL: {oauth_url}")
    return redirect(oauth_url)

@csrf_exempt
def oauth_callback(request, business_subdirectory):  # Add business_subdirectory parameter
    """Handle the OAuth callback from Printful."""
    logger.debug("=== Starting OAuth Callback ===")
    logger.debug(f"Received OAuth callback. GET params: {request.GET}")
    logger.debug(f"Business subdirectory from URL: {business_subdirectory}")
    
    error = request.GET.get('error')
    
    # Handle OAuth errors
    if error:
        logger.error(f"OAuth error received: {error}")
        messages.error(request, f'Printful authorization failed: {error}')
        return redirect('merch_dashboard', business_subdirectory=business_subdirectory)


    # Get code and state from the request
    code = request.GET.get('code')
    state = request.GET.get('state')
    logger.debug(f"Received code and state: {code[:5]}... {state[:5]}...")  # Truncate for security


        # Build the redirect URI
    redirect_uri = settings.PRINTFUL_REDIRECT_URL.format(
        business_subdirectory=business_subdirectory
    )
    logger.debug(f"Built redirect URI: {redirect_uri}")

    
    # Verify state token
    cached_data = cache.get(f'printful_oauth_state_{state}')
    if not cached_data or cached_data.get('user_id') != request.user.id:
        logger.error("Invalid state token or user ID mismatch")
        messages.error(request, 'Invalid authorization state')
        return redirect('merch_dashboard', business_subdirectory=business_subdirectory)
    
    # Verify the business subdirectory matches what was stored in the state
    if cached_data.get('business_subdirectory') != business_subdirectory:
        logger.error(f"Business subdirectory mismatch. Expected: {cached_data.get('business_subdirectory')}, Got: {business_subdirectory}")
        messages.error(request, 'Business mismatch')
        return redirect('merch_dashboard', business_subdirectory=business_subdirectory)
    
    try:
        # Get the business
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        logger.debug(f"Found business: {business.business_name}")

        if request.user != business.owner:
            logger.error(f"Permission denied for user {request.user.id} on business {business_subdirectory}")
            raise PermissionDenied('You do not have permission to connect this business to Printful.')
        
        # Exchange code for access token
        token_data = PrintfulClient.exchange_code_for_token(code, redirect_uri)
        if not token_data or 'access_token' not in token_data:
            raise ValueError('Invalid token data received from Printful.')
        
        # Create or update POD account
        pod_account, created = PODAccount.objects.update_or_create(
            business=business,
            defaults={
                'provider': 'PRINTFUL',
                'api_key': token_data['access_token'],
                'is_active': True
            }
        )
        logger.debug(f"POD account {'created' if created else 'updated'}")

        printful_client = PrintfulClient(pod_account.api_key)
        store_data = {
            'name': business.business_name,  # Use the business name
            'website': f'https://patrons.love/{business_subdirectory}'  # Optional: include website
        }
        logger.debug(f"Attempting to update store with name: {store_data['name']}")
        try:
            store_response = printful_client.update_store(store_data)
            logger.debug(f"Store update successful: {store_response}")
        except Exception as store_error:
            logger.error(f"Store update failed: {str(store_error)}", exc_info=True)
            # Continue execution even if store update fails
        
    except Exception as e:
        logger.error(f"Error in oauth_callback: {str(e)}")
        messages.error(request, f'Error connecting to Printful: {str(e)}')
    
    logger.debug("=== Finishing OAuth Callback ===")
    return redirect('merch_dashboard', business_subdirectory=business_subdirectory)