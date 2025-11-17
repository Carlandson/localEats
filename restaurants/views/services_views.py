# Django core imports
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

# Local imports
from ..models import Business, SubPage, ServicesPage
from ..forms import ServiceForm

@login_required
def create_service(request, business_subdirectory):
    try:
        business = Business.objects.get(subdirectory=business_subdirectory)
        
        # Check if user owns this business
        if business.owner != request.user:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        # Get or create the services page
        subpage = SubPage.objects.get(business=business, page_type='services')
        services_page = getattr(subpage, 'services_content', None)
        if not services_page:
            services_page = ServicesPage.objects.create(subpage=subpage)
            
        form = ServiceForm(request.POST, request.FILES, business=business)
        
        if form.is_valid():
            service = form.save(commit=False)
            service.services_page = services_page  # Set the services_page relationship
            service.save()
            if 'image' in request.FILES:
                image = Image(
                    image=request.FILES['image'],
                    uploaded_by=request.user,
                    content_type=ContentType.objects.get_for_model(service),
                    object_id=service.id,
                    alt_text=service.name
                )
                image.save()
                image_url = image.image.url
            else:
                image_url = None
            return JsonResponse({
                'success': True,
                'message': 'Service created successfully',
                'service': {
                    'id': service.id,
                    'name': service.name,
                    'description': service.description,
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
        return JsonResponse({'error': 'Services page not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def service_detail(request, business_subdirectory, service_id):
    service = get_object_or_404(
        Service, 
        id=service_id, 
        services_page__subpage__business__subdirectory=business_subdirectory
    )
    # Verify business ownership
    if service.services_page.subpage.business.owner != request.user:
        raise PermissionDenied("You don't have permission to access this service")

    if request.method == 'GET':
        return JsonResponse({'service': service.to_dict()})
        
    elif request.method == 'POST':  # Changed from PUT to POST
        try:
            form = ServiceForm(
                request.POST, 
                request.FILES, 
                instance=service,
                business=service.services_page.subpage.business
            )
            
            if form.is_valid():
                service = form.save()

                # Handle image upload if present
                if request.FILES.get('image'):
                    if service.image:
                        service.image.delete()

                # Create new image
                new_image = Image(
                    image=request.FILES['image'],
                    uploaded_by=request.user,
                    content_type=ContentType.objects.get_for_model(service),
                    object_id=service.id,
                    alt_text=service.name
                )
                new_image.save()

                return JsonResponse({
                    'success': True,
                    'message': 'Service updated successfully',
                    'service': service.to_dict()
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
            service.delete()
            return JsonResponse({
                'success': True,
                'message': 'Service deleted successfully'
            })
        except Exception as e:
            return JsonResponse({
                'error': f'Failed to delete service: {str(e)}'
            }, status=500)

@login_required
def get_service_form(request, business_subdirectory, service_id):
    service = get_object_or_404(
        Service.objects.select_related('services_page__subpage__business'), 
        id=service_id, 
        services_page__subpage__business__subdirectory=business_subdirectory
    )
    
    if service.services_page.subpage.business.owner != request.user:
        raise PermissionDenied("You don't have permission to access this service")
        
    form = ServiceForm(instance=service, business=service.services_page.subpage.business)
    
    form_html = render_to_string('forms/edit_service.html', {
        'form': form,
        'service': service,
    }, request=request)
    
    return JsonResponse({
        'success': True,
        'form_html': form_html,
        'current_image_url': service.image.image.url if service.image else None
    })