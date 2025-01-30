from django import forms
from ..models import Product, ProductsPage
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div, HTML
    
class ProductForm(forms.ModelForm):
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
                'accept': 'image/*',
                'class': "mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100",
            }
        ),
        label="Product Image"
    )

    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                'step': '0.01',
                'min': '0',
                'class': "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 focus:ring-2 focus:ring-offset-2 transition-all duration-200",
            }
        ),
        label="Price"
    )

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image']

    def __init__(self, *args, **kwargs):
        self.business = kwargs.pop('business', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_id = 'editProduct' if self.instance.pk else 'createProduct'
        self.helper.form_class = 'space-y-4'
        self.helper.form_method = 'POST'
        self.helper.form_enctype = 'multipart/form-data'
        
        self.helper.layout = Layout(
            Field('name', 
                css_class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 focus:ring-2 focus:ring-offset-2 transition-all duration-200",
                placeholder="Product Name"),
            
            Field('description',
                css_class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 focus:ring-2 focus:ring-offset-2 transition-all duration-200",
                rows="3",
                placeholder="Product Description"),
            
            HTML("<div class='space-y-4'>"),
            HTML("<h3 class='font-medium text-gray-700'>Product Details</h3>"),
            Div(
                Field('price',
                    css_class="mt-1 block w-full",
                    placeholder="0.00"),
                css_class="w-full"
            ),
            HTML("</div>"),
            
            Div(
                HTML('<label class="block text-sm font-medium text-gray-700 mb-2">Product Image</label>'),
                Field('image',
                    template="forms/image_field.html",
                    css_class="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100"),
                css_class="space-y-2"
            ),
            
            Div(
                Submit('submit', 'Create Product', 
                    css_class='px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded transition-colors duration-200 ml-2'),
                css_class='flex justify-end space-x-2 mt-4'
            )
        )

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError("Price cannot be negative")
        return price

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.business:
            instance.business = self.business
        if commit:
            instance.save()
        return instance
