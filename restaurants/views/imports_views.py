"""
Reference file for available imports in the views_refactor package.
This file is for reference only - each view file should import only what it needs.

Example usage in view files:
    from django.shortcuts import render, redirect
    from django.contrib.auth.decorators import login_required
    from ..models import Business, SubPage
    from ..forms import BusinessCreateForm
"""

# Standard library imports
# import json
# import logging

# Third-party imports
# import geopy.distance
# from PIL import Image as PILImage
# import httplib2
# import google_auth_httplib2

# Django core imports
# from django.contrib.auth import authenticate, login, logout, get_user_model
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.contrib.contenttypes.models import ContentType
# from django.core.exceptions import ValidationError, PermissionDenied
# from django.core.paginator import Paginator
# from django.core import serializers
# from django.core.mail import send_mail
# from django.db import IntegrityError, transaction
# from django.db.models import Max
# from django.http import (
#     JsonResponse, HttpResponseRedirect, 
#     HttpResponseBadRequest, HttpResponseForbidden, 
#     HttpResponseNotFound, HttpResponse
# )
# from django.shortcuts import render, redirect, get_object_or_404
# from django.urls import reverse
# from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
# from django.views.decorators.http import require_http_methods, require_POST
# from django.apps import apps
# from django.conf import settings

# Google API imports
# from google.auth.exceptions import RefreshError
# from google.oauth2.credentials import Credentials
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError

# Django Allauth imports
# from allauth.socialaccount.models import SocialAccount

# Local imports - Models
# from ..models import (
#     Image, SubPage, Menu, Course, 
#     Dish, AboutUsPage, EventsPage, 
#     Event, SpecialsPage, Business, 
#     CuisineCategory, SideOption, HomePage, 
#     NewsPost, ContactPage, ContactMessage, 
#     ProductsPage, Product, ServicesPage, 
#     Service, GalleryPage
# )

# Local imports - Forms
# from ..forms import (
#     BusinessCreateForm, BusinessEditForm, BusinessCustomizationForm,
#     ContactMessageForm, ContactPageForm, CustomSignupView,
#     DishSubmit, EventForm, HomePageForm,
#     AboutUsForm, ImageUploadForm, NewsPostForm,
#     ProductForm, ProductPageForm, ServiceForm,
#     ServicePageForm, GalleryPageForm
# )

