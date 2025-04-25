from django.urls import path
from django.conf.urls import include
from .views import custom_signup, custom_logout
from django.conf import settings
from django.conf.urls.static import static
from .admin import business_admin
from . import views
from . import merch

# change to remove views.anything
urlpatterns = [
    # Core pages
    path("", views.index, name="index"),
    path("profile/", views.profile, name="profile"),
    path("aboutus/", views.aboutus, name="aboutus"),
    path("create/", views.create, name="create"),
    
    # Account related
    path('accounts/signup/', custom_signup, name='account_signup'),
    path("accounts/logout/", custom_logout, name="account_logout"),
    path('accounts/', include('allauth.urls')),
    
    # Edit Business Information
    path('<slug:business_subdirectory>/edit-business/', views.edit_business, name="edit_business"),
    path('<slug:business_subdirectory>/edit-business/update/', views.update_business_field, name="update_business_field"),
    
    # Search and filter
    path("search/<str:position>/<str:distance>/", views.search, name="search"),
    path("filter/<str:place>", views.filter, name="filter"),
    
    # API endpoints
    path("fetch_business_info/", views.fetch_business_info, name="fetch_business_info"),
    path('api/<slug:business_subdirectory>/layout/update/', views.update_layout, name='update_layout'),
    
    # Layout and preview endpoints
    path('<slug:business_subdirectory>/layout-editor/', views.layout_editor, name='layout_editor'),
    path('<slug:business_subdirectory>/edit-layout/', views.edit_layout, name='edit_layout'),
    path('<slug:business_subdirectory>/save-layout/', views.save_layout, name='save_layout'),
    
    # Component updates
    path('<slug:business_subdirectory>/update-brand-colors/', views.update_brand_colors, name='update_brand_colors'),
    path('<slug:business_subdirectory>/update-global-component/', views.update_global_component, name='update_global_component'),
    path('<slug:business_subdirectory>/update-hero/', views.update_hero, name='update_hero'),
    
    # Preview related - most specific to least specific
    path('<slug:business_subdirectory>/preview-component/navigation/top-nav/<str:style>/', views.preview_navigation, name='preview_navigation'),
    path('<slug:business_subdirectory>/preview-component/<str:component>/<str:style>/', views.preview_component, name='preview_component_with_style'),
    path('<slug:business_subdirectory>/preview-component/', views.preview_component, name='preview_component'),
    path('<slug:business_subdirectory>/preview-page/<str:page_type>/', views.preview_page, name='preview_page'),
    
    # Image handling
    path('<slug:business_subdirectory>/upload-hero-image/', views.upload_hero_image, name='upload_hero_image'),
    path('<slug:business_subdirectory>/remove-hero-image/', views.remove_hero_image, name='remove_hero_image'),
    
    # Menu management - most specific to least specific
    path('<slug:business_subdirectory>/menu/edit_dish/<int:dishid>/', views.edit_dish, name='edit_dish'),
    path('<slug:business_subdirectory>/menu/delete_course/<int:courseid>/', views.delete_course, name='delete_course'),
    path('<slug:business_subdirectory>/menu/update_course_description/<int:course_id>/', views.update_course_description, name='update_course_description'),
    path('<slug:business_subdirectory>/menu/update_course_note/<int:course_id>/', views.update_course_note, name='update_course_note'),
    path('<slug:business_subdirectory>/menu/side_options/<int:id>/', views.side_options, name='side_options'),
    path('<slug:business_subdirectory>/menu/add_course/', views.add_course, name="add_course"),
    path('<slug:business_subdirectory>/menu/add_dish/', views.add_dish, name="add_dish"),
    path('<slug:business_subdirectory>/menu/', views.menu, name="menu"),
    path("<slug:business_subdirectory>/menu/delete_dish/<int:dishid>/", views.delete_dish, name="delete"),  # Consider making this consistent with other paths
    
    # Menu API endpoints
    # examples
    #path('<slug:business_subdirectory>/menu/get-menu-data/', views.get_menu_data, name='get_menu_data'),
    #path('<slug:business_subdirectory>/menu/get-menu-data/<int:dish_id>/', views.get_menu_data, name='get_menu_data'),
    
    # Page data and content
    path('<slug:business_subdirectory>/get-page-data/<str:page_type>/', views.get_page_data, name='get_page_data'),
    path('<slug:business_subdirectory>/page-content/<str:page_type>/', views.page_content, name='page_content'),
    path('<slug:business_subdirectory>/create/<str:page_type>/', views.create_subpage, name="create_subpage"),
    path('<slug:business_subdirectory>/create-business/', views.create_business, name="create_business"),

    # SEO
    path('<slug:business_subdirectory>/SEO/', views.seo, name="SEO"),
    path('<slug:business_subdirectory>/Advertising/', views.advertising, name="Advertising"),

    # Home Content Editor
    path('<slug:business_subdirectory>/home/settings/', views.update_home_page_settings, name="update_home_page_settings"),
    path('api/<str:business_subdirectory>/news-post/', views.create_news_post, name='create_news_post'),

    # Events Content Editor
    path('<slug:business_subdirectory>/events/add/', views.add_event, name="add_event"),
    path('<str:business_subdirectory>/events/get-form/<int:event_id>/', views.get_event_form, name='get_event_form'),
    path('<str:business_subdirectory>/events/edit/<int:event_id>/', views.edit_event, name='edit_event'),

    # About Content Editor
    path('<slug:business_subdirectory>/about/settings/', views.update_about_page_settings, name="update_about_page_settings"),
    
    # Contact Content Editor
    path('<slug:business_subdirectory>/contact/settings/', views.update_contact_page_settings, name="update_contact_page_settings"),
    
    # Products Content Editor
    path('<slug:business_subdirectory>/products/settings/', views.update_products_page_settings, name="update_products_page_settings"),
    path('<slug:business_subdirectory>/products/create/', views.create_product, name="create_product"),
    path('<slug:business_subdirectory>/products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('<str:business_subdirectory>/products/<int:product_id>/get-form/', views.get_product_form, name='api_product_form'),

    # Services Content Editor
    path('<slug:business_subdirectory>/services/settings/', views.update_services_page_settings, name="update_services_page_settings"),
    path('<slug:business_subdirectory>/services/create/', views.create_service, name="create_service"),
    path('<slug:business_subdirectory>/services/<int:service_id>/', views.service_detail, name='service_detail'),
    path('<str:business_subdirectory>/services/<int:service_id>/get-form/', views.get_service_form, name='api_service_form'),

    # Gallery Content Editor
    path('<str:business_subdirectory>/gallery/upload/', views.upload_gallery_image, name='upload_gallery_image'),
    path('<str:business_subdirectory>/gallery/settings/', views.update_gallery_page_settings, name="update_gallery_page_settings"),
    path('<str:business_subdirectory>/gallery/delete/<int:image_id>/', views.delete_gallery_image, name='delete_gallery_image'),

    # Merch Content Editor
    path('<str:business_subdirectory>/merch/', merch.merch_dashboard, name='merch_dashboard'),
    path('<str:business_subdirectory>/merch/setup-pod-account/', merch.setup_pod_account, name='setup_pod_account'),
    path('<str:business_subdirectory>/merch/callback/', merch.oauth_callback, name='printful_oauth_callback'),
    path('<str:business_subdirectory>/merch/disconnect-pod-account/', merch.disconnect_pod_account, name='disconnect_pod_account'),
    path('<str:business_subdirectory>/merch/create-product/', merch.create_product, name='create_product'),
    path('<str:business_subdirectory>/merch/toggle-product/<int:product_id>/', merch.toggle_product, name='toggle_product'),
    path('<str:business_subdirectory>/merch/product-templates/', merch.get_product_templates, name='get_product_templates'),
    path('<str:business_subdirectory>/merch/connect-printful/', merch.connect_printful, name='connect_printful'),

    # Business pages (catch-all patterns last)
    path('<slug:business_subdirectory>/dashboard/', views.business_dashboard, name="business_dashboard"),
    path('<slug:business_subdirectory>/', views.business_page, name="business_home"),
    path('<slug:business_subdirectory>/<str:page_type>/', views.business_page, name="business_page"),
    path('<slug:business_subdirectory>/events/delete/<int:event_id>/', views.delete_event, name='delete_event'),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)