# Django core imports
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
# Local imports
from ..models import Business, SubPage, ProductsPage
from ..forms import ProductForm

@require_POST
@login_required
def create_product(request, business_subdirectory):
    try:
        business = Business.objects.get(subdirectory=business_subdirectory)
        
        # Check if user owns this business
        if business.owner != request.user:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        # Get or create the products page
        subpage = SubPage.objects.get(business=business, page_type='products')
        products_page = getattr(subpage, 'products_content', None)
        if not products_page:
            products_page = ProductsPage.objects.create(subpage=subpage)
            
        form = ProductForm(request.POST, request.FILES, business=business)
        
        if form.is_valid():
            product = form.save(commit=False)
            product.products_page = products_page  # Set the products_page relationship
            product.save()

            if 'image' in request.FILES:
                image = Image(
                    image=request.FILES['image'],
                    uploaded_by=request.user,
                    content_type=ContentType.objects.get_for_model(product),
                    object_id=product.id,
                    alt_text=product.name
                )
                image.save()
                image_url = image.image.url
            else:
                image_url = None
            
            return JsonResponse({
                'success': True,
                'message': 'Product created successfully',
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                    'price': str(product.price),
                    'image_url': image_url
                }
            })
        else:
            return JsonResponse({
                'error': 'Invalid form data',
                'errors': form.errors
            }, status=400)
            
    except Business.DoesNotExist:
        return JsonResponse({'error': 'Business not found'}, status=404)
    except SubPage.DoesNotExist:
        return JsonResponse({'error': 'Products page not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(['GET', 'POST', 'DELETE'])  # Changed from PUT to POST
def product_detail(request, business_subdirectory, product_id):
    # Get the product and verify ownership
    product = get_object_or_404(
        Product, 
        id=product_id, 
        products_page__subpage__business__subdirectory=business_subdirectory
    )
    
    # Verify business ownership
    if product.products_page.subpage.business.owner != request.user:
        raise PermissionDenied("You don't have permission to access this product")

    if request.method == 'GET':
        return JsonResponse({'product': product.to_dict()})
        
    elif request.method == 'POST':  # Changed from PUT to POST
        try:
            form = ProductForm(
                request.POST, 
                request.FILES, 
                instance=product,
                business=product.products_page.subpage.business
            )
            
            if form.is_valid():
                product = form.save()

                # Handle image upload if present
                if request.FILES.get('image'):
                    if product.image:
                        product.image.delete()
                    product.image = request.FILES['image']
                    product.save()

                return JsonResponse({
                    'success': True,
                    'message': 'Product updated successfully',
                    'product': product.to_dict()
                })
            else:
                return JsonResponse({
                    'error': 'Invalid form data',
                    'errors': form.errors
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
            
    elif request.method == 'DELETE':
        try:
            product.delete()
            return JsonResponse({
                'success': True,
                'message': 'Product deleted successfully'
            })
        except Exception as e:
            return JsonResponse({
                'error': f'Failed to delete product: {str(e)}'
            }, status=500)
        
@login_required
def get_product_form(request, business_subdirectory, product_id):
    product = get_object_or_404(
        Product, 
        id=product_id, 
        products_page__subpage__business__subdirectory=business_subdirectory
    )
    
    if product.products_page.subpage.business.owner != request.user:
        raise PermissionDenied("You don't have permission to access this product")
        
    form = ProductForm(instance=product, business=product.products_page.subpage.business)
    
    form_html = render_to_string('forms/edit_product.html', {
        'form': form,
        'product': product,
    }, request=request)
    
    return JsonResponse({
        'success': True,
        'form_html': form_html,
        'current_image_url': product.image.image.url if product.image else None
    })
