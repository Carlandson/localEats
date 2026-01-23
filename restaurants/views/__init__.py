# Core views
from .core_views import index, profile, aboutus, create_business, edit_business, update_business_field

# Business views
from .business_views import get_business_context, business_dashboard, business_subpage_editor, business_page, business_main, get_business

# Authentication views
from .auth_views import custom_logout
from .auth_views import custom_signup

# Error views
from .errors_views import custom_404

# Menu views
from .menu_views import menu, new_dish, add_course, add_dish, edit_dish, delete_dish, delete_course, get_dish, get_cuisine_categories, update_course_description, update_course_note, side_options

# Layout views
from .layout_views import layout_editor, edit_layout, upload_hero_image, save_layout, get_page_data

# Navigation views
from .navigation_views import search, filter

# Profile views
from .profile_views import profile, create

# Events views
from .events_views import events, get_events_context, delete_event, add_event, get_event_form, edit_event

# Products views
from .products_views import create_product, product_detail, get_product_form

# Services views
from .services_views import create_service, service_detail, get_service_form

# API endpoints
from .apiendpoints_views import some_view, fetch_business_info, update_layout

# Update component views
from .updatecomponent_views import update_brand_colors, update_global_component, update_hero

# Update subpage views
from .updatesubpage_views import update_page_settings, update_products_page_settings, update_services_page_settings, update_gallery_page_settings, update_home_page_settings

# Preview views
from .preview_views import preview_navigation, preview_component, preview_page

# Image handling views
from .imagehandling_views import upload_hero_image, remove_hero_image, upload_gallery_image, delete_gallery_image

# Content views
from .content_views import page_content

# Customize views
from .customize_views import get_editor_context, create_subpage, update_home_page_settings, create_news_post, update_about_page_settings, update_contact_page_settings

# Communication views
from .communication_views import submit_contact_form

# Advert views
from .advert_views import seo, advertising

# Patronage views
from .patronage_portal_views import patronage_portal

# Upload utils
from .upload_utils import check_rate_limit, check_gallery_storage_quota

__all__ = [
    # Core views
    'index',
    'profile', 
    'aboutus',
    'create_business',
    'edit_business',
    'update_business_field',
    
    # Business views
    'get_business_context',
    'business_dashboard',
    'business_subpage_editor',
    'business_page',
    'business_main',
    'get_business',
    
    # Authentication views
    'custom_signup',
    'custom_logout',
    
    # Error views
    'custom_404',

    # Menu views
    'menu',
    'new_dish',
    'add_course',
    'add_dish',
    'edit_dish',
    'delete_dish',
    'delete_course',
    'get_dish',
    'get_cuisine_categories',
    'update_course_description',
    'update_course_note',
    'side_options',
    
    # Layout views
    'layout_editor',
    'edit_layout',
    'upload_hero_image',
    'save_layout',
    'get_page_data',

    # Navigation views
    'search',
    'filter',
    
    # Profile views
    'profile',
    'create',
    
    # Events views
    'events',
    
    # Products views
    'create_product',
    'product_detail',
    'get_product_form',
    
    # Services views
    'create_service',
    'service_detail',
    'get_service_form',
    
    # API endpoints
    'some_view',
    'fetch_business_info',
    'update_layout',
    
    # Update component views
    'update_brand_colors',
    'update_global_component',
    'update_hero',
    
    # Update subpage views
    'update_page_settings',
    'update_products_page_settings',
    # Preview views
    'preview_navigation',
    'preview_component',
    'preview_page',
    'update_services_page_settings',
    'update_gallery_page_settings',
    'update_home_page_settings',
    # Image handling views
    'upload_hero_image',
    'remove_hero_image',
    'upload_gallery_image',
    'delete_gallery_image',
    
    # Content views
    'page_content',
    
    # Customize views
    'get_editor_context',
    'create_subpage',
    'update_home_page_settings',
    'create_news_post',
    'add_event',
    'get_event_form',
    'edit_event',
    'delete_event',
    'update_about_page_settings',
    'update_contact_page_settings',

    # Communication views
    'submit_contact_form',
    
    # Advert views
    'seo',
    'advertising',
]
