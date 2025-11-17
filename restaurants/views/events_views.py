# Django core imports
from django.shortcuts import render, get_object_or_404
import logging

# Local imports
from ..models import Business, SubPage, EventsPage

logger = logging.getLogger(__name__)

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