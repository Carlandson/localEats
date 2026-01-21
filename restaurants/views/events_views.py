import pytz
import logging

# Django core imports
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from crispy_forms.layout import Div, HTML, Submit
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.conf import settings

# Third-party imports
from crispy_forms.layout import Div, HTML, Submit
from PIL import Image as PILImage

# Local imports
from ..models import Business, SubPage, EventsPage
from ..forms import EventForm
from ..models import Image, Event

logger = logging.getLogger(__name__)


def get_events_context(business, subpage):
    """Get events context data - can be called from multiple places"""
    # Get or create events page
    events_page = getattr(subpage, 'events_content', None)
    if not events_page:
        events_page = EventsPage.objects.create(subpage=subpage)
    
    # Get current time in business timezone
    tz = pytz.timezone(business.timezone)
    now = timezone.now().astimezone(tz)
    
    upcoming_events = []
    current_events = []
    past_events = []
    content_type = ContentType.objects.get_for_model(Event)
    
    for event in events_page.events.all().order_by('date'):
        # Convert event dates to business timezone
        event_date = event.date.astimezone(tz)
        event_end_date = event.end_date.astimezone(tz) if event.end_date else None
        
        # Get the associated image for this event
        image = Image.objects.filter(
            content_type=content_type,
            object_id=event.id,
        ).first()
        
        event_data = {
            'id': event.id,
            'title': event.title,
            'datetime': event.date,
            'end_date': event.end_date,
            'description': event.description,
            'image_url': image.image.url if image else None,
        }
        
        # Categorize events
        if event_date > now:
            # Event hasn't started yet
            upcoming_events.append(event_data)
        elif event_end_date and event_end_date >= now:
            # Event has started but hasn't ended
            current_events.append(event_data)
        elif event_end_date is None and event_date <= now:
            # Event has no end date and has started (consider it current if same day, past otherwise)
            if event_date.date() == now.date():
                current_events.append(event_data)
            else:
                past_events.append(event_data)
        else:
            # Event has ended
            past_events.append(event_data)
    
    return {
        'events_page': events_page,
        'upcoming_events': upcoming_events,
        'current_events': current_events,
        'past_events': past_events,
        'form': EventForm(),
    }

def events(request, business_subdirectory):
    business = get_object_or_404(Business, subdirectory=business_subdirectory)
    
    # First get the subpage for this business
    events_subpage = get_object_or_404(SubPage, business=business, page_type='events')
    
    # Use the helper function to get events context
    events_context = get_events_context(business, events_subpage)
    
    context = {
        "business_details": business,
        "business_subdirectory": business_subdirectory,
        "is_owner": request.user == business.owner,
        **events_context  # Unpack all the events context
    }

    if not business.is_verified and request.user != business.owner:
        return render(request, "business_under_construction.html", context)
        
    elif request.user != business.owner:
        return render(request, "visitor_pages/events.html", context)
    
    else:
        return render(request, "owner_subpages/events.html", context)

@login_required
@require_http_methods(["POST"])
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
        form = EventForm(request.POST, request.FILES, business=business)
        logger.info(f"Form data received: {request.POST}")
        logger.info(f"Form is_valid: {form.is_valid()}")
        if not form.is_valid():
            return JsonResponse({
                'success': False,
                'error': form.errors
            }, status=400)
        logger.info(f"Form cleaned_data: {form.cleaned_data}")
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
                logger.error(f"Invalid image file: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid image file'
                })

            try:
                # Create new image
                logger.info(f"Creating new image for event: {event.id}")
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
        response_data = {
            'success': True,
            'event_id': event.id,
            'name': event.title,
            'description': event.description,
            'datetime': event.date.isoformat(),
            'end_datetime': event.end_date.isoformat() if event.end_date else None,
            'image_url': image_url,
            'message': 'Event created successfully'
        }
        logger.info(f"Returning response: {response_data}")
        return JsonResponse(response_data)

    except Exception as e:
        logger.error(f"Error creating event: {str(e)}", exc_info=True)
        return JsonResponse({
            'error': f'An error occurred while creating the event: {str(e)}'
        }, status=500)

@require_http_methods(["POST"])
def edit_event(request, business_subdirectory, event_id):
    try:
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        if request.user != business.owner:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        event = get_object_or_404(Event, id=event_id)
        form = EventForm(request.POST, request.FILES, instance=event, business=business)
        
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
@require_http_methods(["DELETE"])
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

        html = render_to_string('forms/crispy_form.html', {'form': form}, request=request)
        return JsonResponse({'form_html': html})

    except Exception as e:
        logger.error(f"Error in get_event_form: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)