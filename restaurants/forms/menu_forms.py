from django import forms
from ..models import Dish
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div, HTML
import logging

logger = logging.getLogger(__name__)


class DishSubmit(ModelForm):
    class Meta:
        model = Dish
        fields = ['name', 'description', 'price', 'image']  # Changed from image_url to image
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),  # Changed from URLInput to FileInput
        }