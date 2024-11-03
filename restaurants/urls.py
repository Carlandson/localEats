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
    path("search/<str:position>/<str:distance>/", views.search, name="search"),
    path("filter/<str:place>", views.filter, name="filter"),
    path('<slug:eatery>/menu/edit_dish/<int:dishid>/', views.edit_dish, name='edit_dish'),
    path("delete_dish/<int:dishid>", views.delete_dish, name="delete"),
    path('<slug:eatery>/menu/delete_course/<int:courseid>/', views.delete_course, name='delete_course'),
    path('accounts/', include('allauth.urls')),
    path('accounts/signup/', custom_signup, name='account_signup'),
    path("accounts/logout/", custom_logout, name="account_logout"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
