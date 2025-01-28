
from django import forms
from ..models import Image

import logging

logger = logging.getLogger(__name__)

class BusinessImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image', 'alt_text', 'caption']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['alt_text'].help_text = "Use 'logo' for business logo or 'hero' for hero image"


class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image', 'alt_text', 'caption']