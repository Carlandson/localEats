from django.urls import path
from django.conf.urls import include

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("accounts/login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("profile/<str:profile>/", views.profile, name="profile"),
    path("about/", views.about, name="about"),
    path("create/", views.create, name="create"),
    path("eatery/<str:eatery>/", views.eatery, name="eatery"),
    path("add_course/<str:dishData>/<str:eatery>", views.add_course, name="add_course"),
    path("add_dish/<str:eatery>", views.add_dish, name="add_dish"),
    path("search/<str:position>/<str:distance>/", views.search, name="search"),
    path("filter/<str:place>", views.filter, name="filter"),
    path("edit_dish/<int:dishid>", views.edit_dish, name="edit"),
    path("delete_dish/<int:dishid>", views.delete_dish, name="delete"),
    path("delete_course/<str:eatery>/<str:course>", views.delete_course, name="delete_course")
]
