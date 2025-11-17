import logging
import json
# Django core imports
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required


# Local imports
from ..models import (Business, 
    SubPage, HomePage, ServicesPage,
    Image, AboutUsPage, EventsPage, Event, SpecialsPage,
    ContactPage, ProductsPage, Product, Service, GalleryPage,
)
from ..forms import (HomePageForm, 
    NewsPostForm, AboutUsForm, EventForm,
    ContactPageForm, ProductForm, ProductPageForm,
    ServiceForm, ServicePageForm, GalleryPageForm
)

logger = logging.getLogger(__name__)

def get_editor_context(base_context, business, subpage, page_type):
    """Additional context for editor view"""
    context = base_context.copy()
    
    # Add editor-specific data
    context.update({
        'subpages': SubPage.objects.filter(business=business).order_by('page_type'),
        'published_pages': SubPage.get_published_subpages(business),
        'has_menu': SubPage.objects.filter(business=business, page_type='menu').exists(),
    })

    # Add page-specific editor content
    if page_type == 'home':
        # Get or create home page using correct related name
        home_page = getattr(subpage, 'home_content', None)
        if not home_page:
            home_page = HomePage.objects.create(
                subpage=subpage,
                welcome_title=f"Welcome to {business.business_name}",
                welcome_message="We're excited to serve you!"
            )

        context['form'] = HomePageForm(instance=home_page)
        context['news_form'] = NewsPostForm() 
        
        # Add any additional home page data needed
        context['home_data'] = {
            'welcome_title': home_page.welcome_title,
            'welcome_message': home_page.welcome_message,
            'show_welcome': home_page.show_welcome,
            'show_daily_special': home_page.show_daily_special,
            'show_affiliates': home_page.show_affiliates,
            'show_newsfeed': home_page.show_newsfeed,
            'show_upcoming_event': home_page.show_upcoming_event,
            'show_featured_service': home_page.show_featured_service,
            'show_featured_product': home_page.show_featured_product,
        }
    if page_type == 'about':
        about_page = getattr(subpage, 'about_us_content', None)
        if not about_page:
            about_page = AboutUsPage.objects.create(subpage=subpage)
        context['form'] = AboutUsForm(instance=about_page)
    if page_type == 'events':
        # Get or create events page using correct related name
        events_page = getattr(subpage, 'events_content', None)
        if not events_page:
            events_page = EventsPage.objects.create(subpage=subpage)

        events_data = []
        content_type = ContentType.objects.get_for_model(Event)
        
        for event in events_page.events.all().order_by('date'):
            # Get the associated image for this event
            image = Image.objects.filter(
                content_type=content_type,
                object_id=event.id,
            ).first()

            events_data.append({
                'id': event.id,
                'title': event.title,
                'datetime': event.date,
                'end_date': event.end_date,
                'description': event.description,
                'image_url': image.image.url if image else None,
                'is_editable': True
            })

        context['events_data'] = events_data
        context['form'] = EventForm()
    if page_type == 'contact':
        contact_page = getattr(subpage, 'contact_content', None)
        if not contact_page:
            contact_page = ContactPage.objects.create(subpage=subpage)
        context['form'] = ContactPageForm(instance=contact_page)

    if page_type == 'products':
        products_page = getattr(subpage, 'products_content', None)
        if not products_page:
            products_page = ProductsPage.objects.create(
                subpage=subpage,
                description="",  # Default empty description
                show_description=False  # Default value
            )
        context['product_form'] = ProductForm()
        context['products'] = Product.objects.filter(business=business)
        context['description_form'] = ProductPageForm(instance=products_page)
        context['products_page'] = products_page
    if page_type == 'services':
        services_page = getattr(subpage, 'services_content', None)
        if not services_page:
            services_page = ServicesPage.objects.create(
                subpage=subpage,
                description="",
                show_description=False
            )
        context['service_form'] = ServiceForm()
        context['services'] = Service.objects.filter(business=business)
        context['description_form'] = ServicePageForm(instance=services_page)
        context['services_page'] = services_page
    if page_type == 'gallery':
        gallery_page = getattr(subpage, 'gallery_content', None)
        if not gallery_page:
            gallery_page = GalleryPage.objects.create(subpage=subpage)
        
        # Get images with an efficient query
        images = gallery_page.get_images().select_related('uploaded_by').prefetch_related('content_type')
        
        context.update({
            'description_form': GalleryPageForm(instance=gallery_page),
            'gallery_page': gallery_page,
            'images': images,
            'can_upload': True,  # Or whatever permission logic you need
            'max_file_size': Image.MAX_FILE_SIZE,
            'allowed_extensions': Image.ALLOWED_EXTENSIONS,
        })

    elif page_type == 'menu':
        context['menu_data'] = {
            'menus': Menu.objects.filter(business=business).prefetch_related(
                'courses', 
                'courses__dishes'
            ),
            'specials': Dish.objects.filter(menu__business=business, is_special=True),
        }
    return context

def create_subpage(request, business_subdirectory, page_type):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    business = get_object_or_404(Business, subdirectory=business_subdirectory)
    
    # Check if user is owner
    if request.user != business.owner:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    # Check if subpage already exists
    if SubPage.objects.filter(business=business, page_type=page_type).exists():
        return JsonResponse({
            "success": False,
            "error": f'A {page_type} page already exists for this business.'
        }, status=400)

    try:
        # Create a unique slug by adding a timestamp
        timestamp = timezone.now().strftime('%Y%m%d-%H%M%S')
        unique_slug = f"{business.subdirectory}-{page_type}-{timestamp}"

        page_type_display = dict(SubPage.PAGE_TYPES).get(page_type, page_type.title())

        # Create the subpage
        subpage = SubPage.objects.create(
            business=business,
            page_type=page_type,
            title=f"{business.business_name} {page_type_display}",
            slug=unique_slug,
            is_published=True
        )

        # Create the corresponding page content based on type
        if page_type == 'menu':
            Menu.objects.create(
                business=business,
                name=f"{business.business_name} Menu",
                subpage=subpage
            )
        elif page_type == 'about':
            AboutUsPage.objects.create(
                subpage=subpage,
                content=""
            )
        elif page_type == 'events':
            EventsPage.objects.create(
                subpage=subpage
            )
        elif page_type == 'specials':
            SpecialsPage.objects.create(
                subpage=subpage
            )

        return JsonResponse({
            "success": True,
            "message": f'{page_type.title()} page created successfully!',
            "page_type": page_type,
            "slug": subpage.slug,
            "url": reverse(page_type, kwargs={'business_subdirectory': business_subdirectory})
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)
    

def about(request, business_subdirectory):
    business = get_object_or_404(Business, subdirectory=business_subdirectory)
    
    # First get the subpage for this business
    about_subpage = get_object_or_404(SubPage, business=business, page_type='about')
    
    # Then get the about page associated with this subpage
    about_page = get_object_or_404(AboutUsPage, subpage=about_subpage)
    
    context = {
        "business_details": business,
        "business_subdirectory": business_subdirectory,
        "about_page": about_page,
        "owner": request.user == business.owner,
    }

    if not business.is_verified and request.user != business.owner:
        return render(request, "business_under_construction.html", context)
        
    elif request.user != business.owner:
        return render(request, "visitor_pages/about.html", context)
    
    else:
        return render(request, "owner_subpages/about.html", context)

def specials(request, business_subdirectory):
    business = get_object_or_404(Business, subdirectory=business_subdirectory)
    
    # First get the subpage for this business
    specials_subpage = get_object_or_404(SubPage, business=business, page_type='specials')
    
    # Then get the specials page associated with this subpage
    specials_page = get_object_or_404(SpecialsPage, subpage=specials_subpage)
    
    context = {
        "business_details": business,
        "business_subdirectory": business_subdirectory,
        "specials_page": specials_page,
        "owner": request.user == business.owner,
    }

    if not business.is_verified and request.user != business.owner:
        return render(request, "business_under_construction.html", context)
        
    elif request.user != business.owner:
        return render(request, "visitor_pages/specials.html", context)
    
    else:
        return render(request, "owner_subpages/specials.html", context)
    
def events(request, business_subdirectory):
    business = get_object_or_404(Business, subdirectory=business_subdirectory)
    
    # First get the subpage for this business
    events_subpage = get_object_or_404(SubPage, business=business, page_type='events')
    
    # Then get the events page associated with this subpage
    events_page = get_object_or_404(EventsPage, subpage=events_subpage)
    
    context = {
        "business_details": business,
        "business_subdirectory": business_subdirectory,
        "events_page": events_page,
        "owner": request.user == business.owner,
    }

    if not business.is_verified and request.user != business.owner:
        return render(request, "business_under_construction.html", context)
        
    elif request.user != business.owner:
        return render(request, "visitor_pages/events.html", context)
    
    else:
        return render(request, "owner_subpages/events.html", context)
    
@login_required
def add_event(request, business_subdirectory):
    """Add a new event to the business's events page"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required.'}, status=400)

    # Get the business and verify ownership
    business = get_object_or_404(Business, subdirectory=business_subdirectory)
    if request.user != business.owner:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        # Get or create events page
        subpage = SubPage.objects.get_or_create(
            business=business,
            page_type='events'
        )[0]
        events_page = EventsPage.objects.get_or_create(subpage=subpage)[0]

        # Get form data
        form = EventForm(request.POST, request.FILES)
        if not form.is_valid():
            return JsonResponse({
                'success': False,
                'error': form.errors
            }, status=400)

        # Create new event using form's cleaned data
        event = form.save(commit=False)
        event.events_page = events_page
        event.save()

        # Handle image if provided
        image_url = None
        if 'image' in request.FILES:
            image_file = request.FILES['image']
            
            # Check file size
            if image_file.size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                event.delete()  # Clean up the created event
                return JsonResponse({
                    'success': False, 
                    'error': f'File size cannot exceed {settings.FILE_UPLOAD_MAX_MEMORY_SIZE // (1024*1024)}MB'
                })

            # Check file extension
            ext = image_file.name.split('.')[-1].lower()
            if ext not in Image.ALLOWED_EXTENSIONS:
                event.delete()  # Clean up the created event
                return JsonResponse({
                    'success': False,
                    'error': f'Unsupported file extension. Allowed types: {", ".join(Image.ALLOWED_EXTENSIONS)}'
                })
            
            # Validate image file
            try:
                with PILImage.open(image_file) as img:
                    img.verify()
                    image_file.seek(0)  # Reset file pointer after verify
            except Exception as e:
                event.delete()  # Clean up the created event
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid image file'
                })

            try:
                # Create new image
                image = Image.objects.create(
                    image=image_file,
                    uploaded_by=request.user,
                    content_type=ContentType.objects.get_for_model(event),
                    object_id=event.id,
                    alt_text=f"Event image for {event.title}"
                )
                image_url = image.image.url
                
            except ValidationError as e:
                event.delete()  # Clean up the created event
                logger.error(f"Validation error during event image upload: {str(e)}")
                if hasattr(e, 'message_dict'):
                    error_message = '; '.join([f"{k}: {', '.join(v)}" for k, v in e.message_dict.items()])
                else:
                    error_message = str(e)
                return JsonResponse({
                    'success': False,
                    'error': error_message
                })

        # Return the created event data
        return JsonResponse({
            'success': True,
            'event_id': event.id,
            'name': event.title,
            'description': event.description,
            'datetime': event.date.isoformat(),
            'end_datetime': event.end_date.isoformat() if event.end_date else None,
            'image_url': image_url,
            'message': 'Event created successfully'
        })

    except Exception as e:
        logger.error(f"Error creating event: {str(e)}", exc_info=True)
        return JsonResponse({
            'error': f'An error occurred while creating the event: {str(e)}'
        }, status=500)
    
@require_http_methods(["GET"])
def get_event_form(request, business_subdirectory, event_id):
    try:
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        if request.user != business.owner:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        event = get_object_or_404(Event, id=event_id)
        
        # Get the current image
        content_type = ContentType.objects.get_for_model(Event)
        current_image = Image.objects.filter(
            content_type=content_type,
            object_id=event.id
        ).first()

        tz = pytz.timezone(business.timezone)
        local_date = event.date.astimezone(tz)
        local_end_date = event.end_date.astimezone(tz) if event.end_date else None

        form = EventForm(instance=event, business=business, initial={
            'start_date': event.date.date(),
            'start_time': event.date.time(),
            'end_date': event.end_date.date() if event.end_date else None,
            'end_time': event.end_date.time() if event.end_date else None,
        })
        
        form.helper.form_id = f'editEvent{event_id}'
        
        # Add image preview if exists
        if current_image:
            form.helper.layout.insert(-1, Div(
                HTML(f"""
                    <div class="mb-4">
                        <p class="text-sm text-gray-600 mb-2">Current Image:</p>
                        <img src="{current_image.image.url}" 
                             alt="Current event image" 
                             class="h-32 w-32 object-cover rounded-lg border border-gray-200">
                    </div>
                """),
                css_class='mt-4'
            ))

        form.helper.layout[-1] = Div(
            HTML(f"""
                <button type="button" class="cancel-edit px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded transition-colors duration-200">
                    Cancel
                </button>
            """),
            Submit('submit', 'Save Changes', 
                css_class='px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded transition-colors duration-200 ml-2'),
            css_class='flex justify-end space-x-2 mt-4'
        )

        html = render_to_string('forms/crispy_form.html', {'form': form})
        return JsonResponse({'form_html': html})

    except Exception as e:
        logger.error(f"Error in get_event_form: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
    

@require_http_methods(["POST"])
def edit_event(request, business_subdirectory, event_id):
    try:
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        if request.user != business.owner:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        event = get_object_or_404(Event, id=event_id)
        form = EventForm(request.POST, request.FILES, instance=event)
        
        if form.is_valid():
            event = form.save()

            # Handle image upload if present
            if request.FILES.get('image'):
                content_type = ContentType.objects.get_for_model(Event)
                
                # Delete old image if exists
                Image.objects.filter(
                    content_type=content_type,
                    object_id=event.id
                ).delete()
                
                # Create new image
                Image.objects.create(
                    image=request.FILES['image'],
                    uploaded_by=request.user,
                    content_type=content_type,
                    object_id=event.id,
                    alt_text=f"Event image for {event.title}"
                )

            return JsonResponse({
                'success': True,
                'message': 'Event updated successfully'
            })
        else:
            return JsonResponse({
                'error': 'Invalid form data',
                'form_errors': form.errors
            }, status=400)

    except Exception as e:
        logger.error(f"Error in edit_event: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
    
@login_required
@require_http_methods(["POST"])
def delete_event(request, business_subdirectory, event_id):
    """Delete an event after verifying ownership and permissions"""
    try:
        # Get the business and verify ownership
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        if request.user != business.owner:
            return JsonResponse({
                'success': False,
                'error': 'Unauthorized: You do not own this business'
            }, status=403)

        # Get the event and verify it belongs to the business
        event = get_object_or_404(Event, 
            id=event_id,
            events_page__subpage__business=business
        )

        # Delete associated image if it exists
        content_type = ContentType.objects.get_for_model(Event)
        Image.objects.filter(
            content_type=content_type,
            object_id=event.id
        ).delete()

        # Delete the event
        event.delete()

        return JsonResponse({
            'success': True,
            'message': 'Event deleted successfully'
        })

    except Event.DoesNotExist:
        logger.warning(f"Attempted to delete non-existent event {event_id}")
        return JsonResponse({
            'success': False,
            'error': 'Event not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error deleting event {event_id}: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while deleting the event'
        }, status=500)
    

@login_required
@require_http_methods(["POST"])
def update_home_page_settings(request, business_subdirectory):
    print(business_subdirectory)
    try:
        data = json.loads(request.body)
        subpage = SubPage.objects.get(business__subdirectory=business_subdirectory, page_type='home')
        print(subpage)
        home_page, created = HomePage.objects.get_or_create(subpage=subpage)

        # Handle welcome section update
        if data.get('fieldName') == 'show_welcome' and ('welcome_title' in data or 'welcome_message' in data):
            home_page.welcome_title = data.get('welcome_title', home_page.welcome_title)
            home_page.welcome_message = data.get('welcome_message', home_page.welcome_message)
            home_page.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Welcome content updated successfully',
                'welcome_title': home_page.welcome_title,
                'welcome_message': home_page.welcome_message
            })

        # Handle boolean toggle updates
        field_name = data.get('fieldName')
        new_value = data.get('value')
        
        allowed_fields = [
            'show_welcome',
            'show_daily_special',
            'show_affiliates',
            'show_newsfeed',
            'show_upcoming_event',
            'show_featured_service',
            'show_featured_product'
        ]
        
        if field_name not in allowed_fields:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid field name'
            }, status=400)
        
        setattr(home_page, field_name, new_value)
        home_page.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Setting updated successfully',
            'field': field_name,
            'value': new_value
        })

    except SubPage.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Subpage not found'
        }, status=404)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
    
@login_required
@require_http_methods(["POST"])
def create_news_post(request, business_subdirectory):
    try:
        subpage = SubPage.objects.get(business__subdirectory=business_subdirectory, page_type='home')
        home_page = HomePage.objects.get(subpage=subpage)
        
        form = NewsPostForm(request.POST, request.FILES)
        if form.is_valid():
            news_post = form.save(commit=False)
            news_post.news_feed = home_page.news_feed
            news_post.save()

            # Handle image if present
            if 'image' in request.FILES:
                image = Image(
                    image=request.FILES['image'],
                    uploaded_by=request.user,
                    content_object=news_post,
                    alt_text=f"Image for {news_post.title}"
                )
                image.save()

            messages.success(request, 'News post created successfully!')
            return redirect('home_page', business_subdirectory=business_subdirectory)
        else:
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'subpages/home.html', {
                'form': form,
                'news_form': form,  # Add both since your template might use either
            })

    except (SubPage.DoesNotExist, HomePage.DoesNotExist):
        messages.error(request, 'Page not found')
        return redirect('home')

@login_required
@require_http_methods(["POST"])
def update_about_page_settings(request, business_subdirectory):

    try:
        data = json.loads(request.body)
        subpage = SubPage.objects.get(business__subdirectory=business_subdirectory, page_type='about')
        about_page, created = AboutUsPage.objects.get_or_create(subpage=subpage)
        print(data.get('fieldName'))
        # Handle content section updates
        if data.get('fieldName') in ['content', 'history', 'team_members', 'mission_statement', 'core_values']:
            field_name = data.get('fieldName')
            print(field_name)
            setattr(about_page, field_name, data.get(field_name, getattr(about_page, field_name)))
            about_page.save()
            return JsonResponse({
                'status': 'success',
                'message': f'{field_name.replace("_", " ").title()} updated successfully',
                field_name: getattr(about_page, field_name)
            })

        # Handle boolean toggle updates
        field_name = data.get('fieldName')
        new_value = data.get('value')
        
        allowed_fields = [
            'show_history',
            'show_team',
            'show_mission',
            'show_values',
            'team_members',
            'core_values',
            'mission_statement',
            'history'
        ]
        
        if field_name not in allowed_fields:
            print(data.get('fieldName'))
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid field name'
            }, status=400)
        
        setattr(about_page, field_name, new_value)
        about_page.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Setting updated successfully',
            'field': field_name,
            'value': new_value
        })

    except SubPage.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Subpage not found'
        }, status=404)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
    
@login_required
@require_http_methods(["POST"])
def update_contact_page_settings(request, business_subdirectory):
    try:
        data = json.loads(request.body)
        subpage = SubPage.objects.get(
            business__subdirectory=business_subdirectory,
            business__owner=request.user,  # Ensure owner
            page_type='contact'
        )
        contact_page, created = ContactPage.objects.get_or_create(subpage=subpage)

        # Handle content updates
        if data.get('fieldName') == 'description':
            contact_page.description = data.get('description', contact_page.description)
            contact_page.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Description updated successfully',
                'description': contact_page.description
            })

        # Handle boolean toggle updates
        field_name = data.get('fieldName')
        new_value = data.get('value')
        
        allowed_fields = [
            'show_description',
            'show_map',
            'show_contact_form',
            'description'
        ]
        
        if field_name not in allowed_fields:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid field name'
            }, status=400)
        
        setattr(contact_page, field_name, new_value)
        contact_page.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Setting updated successfully',
            'field': field_name,
            'value': new_value
        })

    except SubPage.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Contact page not found'
        }, status=404)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
    
@login_required
def edit_business(request, business_subdirectory):
    business = get_object_or_404(Business, subdirectory=business_subdirectory, owner=request.user)
    
    if request.method == 'POST':
        print(request.POST)
        form = BusinessEditForm(request.POST, instance=request.user.business)
        if form.is_valid():
            business = form.save()
            # Return only the updated field value
            field_name = next(iter(form.changed_data))  # Get the first (and should be only) changed field
            return JsonResponse({
                field_name: getattr(business, field_name)
            })
        return JsonResponse({'error': 'Invalid form data'}, status=400)
    else:
        form = BusinessEditForm(instance=business)
    
    return render(request, 'subpages/edit_business.html', {
        'form': form,
        'instance': business,
        'business_details': business,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
        'is_edit_page': True,
        'is_owner': True,
    })

@login_required
def update_business_field(request, business_subdirectory):
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    business = get_object_or_404(Business, subdirectory=business_subdirectory)
    
    # Get the field being updated from the request
    field_name = request.POST.get('field_name')
    if not field_name:
        return JsonResponse({'error': 'No field specified'}, status=400)
    
    # Get the new value
    new_value = request.POST.get(field_name)
    current_value = str(getattr(business, field_name))

    # If the value hasn't changed, return success without doing anything
    if new_value == current_value:
        return JsonResponse({
            'status': 'success',
            field_name: current_value
        })
    
    # Create a form with only the specific field data
    form_data = {field_name: new_value}
    form = BusinessEditForm(form_data, instance=business)
    
    # Validate only the specific field
    form.fields = {field_name: form.fields[field_name]}
    
    if form.is_valid():
        try:
            # If updating address, check for existing verified business
            if field_name == 'address':
                new_address = form.cleaned_data[field_name]
                existing_business = Business.objects.filter(
                    address=new_address,
                    is_verified=True
                ).exclude(id=business.id).first()
                
                if existing_business:
                    return JsonResponse({
                        'status': 'error',
                        'errors': ['A verified business already exists at this address. Please contact support if this is your business.']
                    }, status=400)
            
            # Update the field if validation passes
            setattr(business, field_name, form.cleaned_data[field_name])
            business.save(update_fields=[field_name])
            
            return JsonResponse({
                'status': 'success',
                field_name: str(getattr(business, field_name))
            })
            
        except ValidationError as e:
            return JsonResponse({
                'status': 'error',
                'errors': [str(e)]
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'errors': ['An unexpected error occurred. Please try again.']
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'errors': form.errors.get(field_name, ['Invalid data'])
    }, status=400)