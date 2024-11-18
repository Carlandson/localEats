from django.urls import path
from django.conf.urls import include
from .views import custom_signup, custom_logout
from django.conf import settings
from django.conf.urls.static import static
from . import views

# change to remove views.anything
urlpatterns = [
    path("", views.index, name="index"),
    path("profile/", views.profile, name="profile"),
    path("aboutus/", views.aboutus, name="aboutus"),
    path("create/", views.create, name="create"),
    path("fetch_business_info/", views.fetch_business_info, name="fetch_business_info"),
    path("<slug:business_subdirectory>/", views.business_main, name="business_subdirectory"),
    path("<slug:business_subdirectory>/menu/", views.menu, name="menu"),
    path("<slug:business_subdirectory>/about/", views.about, name="about"),
    path("<slug:business_subdirectory>/specials/", views.specials, name="specials"),
    path("<slug:business_subdirectory>/events/", views.events, name="events"),
    path("<slug:business_subdirectory>/menu/add_course/", views.add_course, name="add_course"),
    path("<slug:business_subdirectory>/create/<str:page_type>/", views.create_subpage, name="create_subpage"),
    path("<slug:business_subdirectory>/menu/add_dish/", views.add_dish, name="add_dish"),
    path('<str:business_subdirectory>/menu/update_course_description/<int:course_id>/', views.update_course_description, name='update_course_description'),
    path('<str:business_subdirectory>/menu/update_course_note/<int:course_id>/', views.update_course_note, name='update_course_note'),
    path('<str:business_subdirectory>/menu/side_options/<int:id>/', views.side_options, name='side_options'),
    path("search/<str:position>/<str:distance>/", views.search, name="search"),
    path("filter/<str:place>", views.filter, name="filter"),
    path('<slug:business_subdirectory>/menu/edit_dish/<int:dishid>/', views.edit_dish, name='edit_dish'),
    path("delete_dish/<int:dishid>", views.delete_dish, name="delete"),
    path('<slug:business_subdirectory>/menu/delete_course/<int:courseid>/', views.delete_course, name='delete_course'),
    path('<str:business_subdirectory>/edit-layout/', views.edit_layout, name='edit_layout'),
    path('<str:business_subdirectory>/preview-component/<str:component>/<str:style>/', views.preview_component, name='preview_component'),
    path('<str:business_subdirectory>/save-layout/', views.save_layout, name='save_layout'),
    path('accounts/', include('allauth.urls')),
    path('accounts/signup/', custom_signup, name='account_signup'),
    path("accounts/logout/", custom_logout, name="account_logout"),
    path('<str:business_subdirectory>/get-page-data/<str:page_type>/', views.get_page_data, name='get_page_data'),
    path('<str:business_subdirectory>/update-hero/', views.update_hero, name='update_hero'),
    path('<str:business_subdirectory>/preview-component/navigation/top-nav/<str:style>/', views.preview_navigation, name='preview_navigation'),
    path('<str:business_subdirectory>/preview-page/<str:page_type>/', views.preview_page, name='preview_page'),
    path('<str:business_subdirectory>/upload-hero-image/', views.upload_hero_image, name='upload_hero_image'),
    path('<str:business_subdirectory>/remove-hero-image/', views.remove_hero_image, name='remove_hero_image'),
    path('<str:business_subdirectory>/update-global-component/', views.update_global_component, name='update_global_component'),
    path('<str:business_subdirectory>/page-content/<str:page_type>/', views.page_content, name='page_content'),
    path('<str:business_subdirectory>/layout-editor/', views.layout_editor, name='layout_editor'),
    path('<str:business_subdirectory>/update-brand-colors/', views.update_brand_colors, name='update_brand_colors'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
