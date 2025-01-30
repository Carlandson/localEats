
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div, HTML
from ..models import Service


class ServiceForm(forms.ModelForm):
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
                'accept': 'image/*',
                'class': "mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100",
            }
        ),
        label="Service Image"
    )

    featured = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': "h-4 w-4 rounded border-gray-300 text-emerald-600 focus:ring-emerald-500",
            }
        ),
        label="Featured Service"
    )

    class Meta:
        model = Service
        fields = ['name', 'description', 'featured']

    def __init__(self, *args, instance=None, **kwargs):
        self.business = kwargs.pop('business', None)
        super().__init__(*args, instance=instance, **kwargs)
        if instance and instance.image:
            # Add the current image URL to the form context
            self.current_image_url = instance.image.image.url
        self.helper = FormHelper()
        self.helper.form_id = 'editService' if self.instance.pk else 'createService'
        self.helper.form_class = 'space-y-4'
        self.helper.form_method = 'POST'
        self.helper.form_enctype = 'multipart/form-data'
        
        self.helper.layout = Layout(
            Field('name', 
                css_class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 focus:ring-2 focus:ring-offset-2 transition-all duration-200",
                placeholder="Service Name"),
            
            Field('description',
                css_class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 focus:ring-2 focus:ring-offset-2 transition-all duration-200",
                rows="3",
                placeholder="Service Description"),
            
            HTML("<div class='space-y-4'>"),
            HTML("<h3 class='font-medium text-gray-700'>Service Details</h3>"),
            Div(
                Field('featured'),
                HTML('<label for="id_featured" class="ml-2 text-sm text-gray-700">Featured Service</label>'),
                css_class="flex items-center"
            ),
            HTML("</div>"),
            
            Div(
                HTML('<label class="block text-sm font-medium text-gray-700 mb-2">Service Image</label>'),
                Field('image',
                    template="forms/image_field.html",
                    css_class="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100"),
                css_class="space-y-2"
            ),
            
            Div(
                Submit('submit', 'Create Service', 
                    css_class='px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded transition-colors duration-200 ml-2'),
                css_class='flex justify-end space-x-2 mt-4'
            )
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.business:
            instance.business = self.business
        if commit:
            instance.save()
        return instance