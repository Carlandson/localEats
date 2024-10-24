from django.urls import path
from django.conf.urls import include
from .views import custom_signup, custom_logout
from . import views

# change to remove views.anything
urlpatterns = [
    path("", views.index, name="index"),
    path("profile/", views.profile, name="profile"),
    path("about/", views.about, name="about"),
    path("create/", views.create, name="create"),
    path("fetch_business_info/", views.fetch_business_info, name="fetch_business_info"),
    path("<slug:eatery>/", views.eatery, name="eatery"),
    path("add_course/<str:dishData>/<str:eatery>", views.add_course, name="add_course"),
    path("add_dish/<str:eatery>", views.add_dish, name="add_dish"),
    path("search/<str:position>/<str:distance>/", views.search, name="search"),
    path("filter/<str:place>", views.filter, name="filter"),
    path("edit_dish/<int:dishid>", views.edit_dish, name="edit"),
    path("delete_dish/<int:dishid>", views.delete_dish, name="delete"),
    path("delete_course/<str:eatery>/<str:course>", views.delete_course, name="delete_course"),
    path('accounts/', include('allauth.urls')),
    path('accounts/signup/', custom_signup, name='account_signup'),
    path("accounts/logout/", custom_logout, name="account_logout"),
]
