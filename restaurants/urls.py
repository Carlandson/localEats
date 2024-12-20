from django.urls import path
from django.conf.urls import include
from .views import custom_signup, custom_logout
from django.conf import settings
from django.conf.urls.static import static
from . import views

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
    path("delete_dish/<int:dishid>", views.delete_dish, name="delete"),  # Consider making this consistent with other paths
    
    # Page data and content
    path('<slug:business_subdirectory>/get-page-data/<str:page_type>/', views.get_page_data, name='get_page_data'),
    path('<slug:business_subdirectory>/page-content/<str:page_type>/', views.page_content, name='page_content'),
    path('<slug:business_subdirectory>/create/<str:page_type>/', views.create_subpage, name="create_subpage"),
    
    # Business pages (catch-all patterns last)
    path('<slug:business_subdirectory>/', views.business_page, name="business_home"),
    path('<slug:business_subdirectory>/<str:page_type>/', views.business_page, name="business_page"),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)