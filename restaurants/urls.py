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
    path("<slug:eatery>/", views.eatery, name="eatery"),
    path("<slug:eatery>/menu/", views.menu, name="menu"),
    path("<slug:eatery>/about/", views.about, name="about"),
    path("<slug:eatery>/specials/", views.specials, name="specials"),
    path("<slug:eatery>/events/", views.events, name="events"),
    path("<slug:eatery>/menu/add_course/", views.add_course, name="add_course"),
    path("<slug:eatery>/create/<str:page_type>/", views.create_subpage, name="create_subpage"),
    path("<slug:eatery>/menu/add_dish/", views.add_dish, name="add_dish"),
    path('<str:eatery>/menu/update_course_description/<int:course_id>/', views.update_course_description, name='update_course_description'),
    path('<str:eatery>/menu/update_course_note/<int:course_id>/', views.update_course_note, name='update_course_note'),
    path('<str:eatery>/menu/side_options/<int:id>/', views.side_options, name='side_options'),
    path("search/<str:position>/<str:distance>/", views.search, name="search"),
    path("filter/<str:place>", views.filter, name="filter"),
    path('<slug:eatery>/menu/edit_dish/<int:dishid>/', views.edit_dish, name='edit_dish'),
    path("delete_dish/<int:dishid>", views.delete_dish, name="delete"),
    path('<slug:eatery>/menu/delete_course/<int:courseid>/', views.delete_course, name='delete_course'),
    path('<str:eatery>/preview/', views.preview_restaurant, name='preview_restaurant'),
    path('<str:eatery>/menu/preview/', views.preview_menu, name='preview_menu'),
    path('<str:eatery>/events/preview/', views.preview_events, name='preview_events'),
    path('<str:eatery>/about/preview/', views.preview_about, name='preview_about'),
    path('<str:eatery>/edit-layout/', views.edit_layout, name='edit_layout'),
    path('<str:eatery>/preview-component/<str:component>/<str:style>/', views.preview_component, name='preview_component'),
    path('<str:eatery>/save-layout/', views.save_layout, name='save_layout'),
    path('accounts/', include('allauth.urls')),
    path('accounts/signup/', custom_signup, name='account_signup'),
    path("accounts/logout/", custom_logout, name="account_logout"),
    path('<str:eatery>/get-page-data/<str:page_type>/', views.get_page_data, name='get_page_data'),
    path('<str:eatery>/update-hero/', views.update_hero, name='update_hero'),
    path('<str:eatery>/preview-component/navigation/top-nav/<str:style>/', views.preview_navigation, name='preview_navigation'),
    path('<str:eatery>/preview-page/<str:page_type>/', views.preview_page, name='preview_page'),
    path('<str:eatery>/upload-hero-image/', views.upload_hero_image, name='upload_hero_image'),
    path('<str:eatery>/remove-hero-image/', views.remove_hero_image, name='remove_hero_image'),
    path('<str:eatery>/update-global-component/', views.update_global_component, name='update_global_component'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
