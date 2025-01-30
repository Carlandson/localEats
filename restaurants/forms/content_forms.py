from django import forms
from ..models import NewsPost, AboutUsPage, ContactMessage, ContactPage, HomePage, ProductsPage, ServicesPage, GalleryPage
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div, HTML
import logging

logger = logging.getLogger(__name__)
# Home Page Form
class HomePageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        # Add Tailwind classes to form fields
        self.fields['welcome_title'].widget.attrs.update({
            'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
        })
        self.fields['welcome_message'].widget.attrs.update({
            'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            'rows': 4
        })
        
        self.helper.layout = Layout(
            Field('welcome_title', placeholder='Enter welcome title'),
            Field('welcome_message', placeholder='Enter welcome message'),
            Submit('submit', 'Save Changes', css_class='mt-4 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500')
        )

    class Meta:
        model = HomePage
        fields = [
            'welcome_title',
            'welcome_message',
            'show_welcome',
            'show_daily_special',
            'show_affiliates',
            'show_newsfeed',
            'show_upcoming_event',
            'show_featured_service',
            'show_featured_product'
        ]
        labels = {
            'show_welcome': 'Show Welcome Section',
            'show_daily_special': 'Show Daily Special',
            'show_affiliates': 'Show Affiliates',
            'show_newsfeed': 'Show News Feed',
            'show_upcoming_event': 'Show Upcoming Event',
            'show_featured_service': 'Show Featured Service',
            'show_featured_product': 'Show Featured Product'
        }

class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input rounded-md'}),
            'email': forms.EmailInput(attrs={'class': 'form-input rounded-md'}),
            'subject': forms.TextInput(attrs={'class': 'form-input rounded-md'}),
            'message': forms.Textarea(attrs={'class': 'form-textarea rounded-md', 'rows': 4}),
        }

class ContactPageForm(forms.ModelForm):
    class Meta:
        model = ContactPage
        fields = ['description', 'show_description', 'show_map', 'show_contact_form']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'show_description': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 rounded border-gray-300 text-emerald-600 focus:ring-emerald-500'
            }),
            'show_map': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 rounded border-gray-300 text-emerald-600 focus:ring-emerald-500'
            }),
            'show_contact_form': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 rounded border-gray-300 text-emerald-600 focus:ring-emerald-500'
            }),
        }

class NewsPostForm(forms.ModelForm):
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
                'accept': 'image/*',
                'class': "mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100",
            }
        ),
        label="Post Image"
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'  # Important for file uploads

        
        # Add Tailwind classes to form fields
        self.fields['title'].widget.attrs.update({
            'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            'placeholder': 'Enter news title'
        })
        self.fields['content'].widget.attrs.update({
            'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            'rows': 4,
            'placeholder': 'Enter news content'
        })
        
        self.helper.layout = Layout(
            Field('title', placeholder='Enter news title'),
            Field('content', placeholder='Enter news content'),
            Field('image',
                css_class="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"),
            Submit('submit', 'Post News', css_class='mt-4 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500')
        )

    class Meta:
        model = NewsPost
        fields = ['title', 'content', 'image']

class AboutUsForm(forms.ModelForm):
    # Main content fields
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full rounded-lg border-gray-300 focus:border-indigo-500 focus:ring-indigo-500',
            'rows': 4,
            'placeholder': 'Tell your story...'
        }),
        label="About Us Content",
        help_text="Share your business's main story and values"
    )
    
    history = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full rounded-lg border-gray-300 focus:border-indigo-500 focus:ring-indigo-500',
            'rows': 4,
            'placeholder': 'Share your history...'
        }),
        label="Our History",
        required=False,
        help_text="Tell the story of how your business started"
    )
    
    team_members = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full rounded-lg border-gray-300 focus:border-indigo-500 focus:ring-indigo-500',
            'rows': 4,
            'placeholder': 'Introduce your team...'
        }),
        label="Team Members",
        required=False,
        help_text="Introduce key team members"
    )

    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
                'accept': 'image/*',
                'class': "mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100",
            }
        ),
        label="Team Image",
        help_text="Upload an image of your team or business"
    )

    # Toggle fields for sections
    show_history = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500',
        }),
        label="Show History Section"
    )

    show_team = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500',
        }),
        label="Show Team Section"
    )

    # Mission and values (optional sections)
    mission_statement = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full rounded-lg border-gray-300 focus:border-indigo-500 focus:ring-indigo-500',
            'rows': 3,
            'placeholder': 'Our mission is...'
        }),
        required=False,
        label="Mission Statement",
        help_text="Share your business's mission"
    )

    core_values = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full rounded-lg border-gray-300 focus:border-indigo-500 focus:ring-indigo-500',
            'rows': 3,
            'placeholder': 'Our core values...'
        }),
        required=False,
        label="Core Values",
        help_text="List your business's core values"
    )

    show_mission = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500',
        }),
        label="Show Mission Statement"
    )

    show_values = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500',
        }),
        label="Show Core Values"
    )

    class Meta:
        model = AboutUsPage
        fields = [
            'content',
            'history',
            'team_members',
            'image',
            'show_history',
            'show_team',
            'mission_statement',
            'core_values',
            'show_mission',
            'show_values'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't render form tag, we'll handle it in template
        
        # Add any additional initialization if needed
        for field in self.fields.values():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({
                    'class': 'w-full rounded-lg border-gray-300 focus:border-indigo-500 focus:ring-indigo-500'
                })

class ProductPageForm(forms.ModelForm):
    class Meta:
        model = ProductsPage
        fields = ['description']

class ServicePageForm(forms.ModelForm):
    class Meta:
        model = ServicesPage
        fields = ['description']
    
class GalleryPageForm(forms.ModelForm):
    class Meta:
        model = GalleryPage
        fields = ['description', 'show_description']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 4
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't generate form tag
        self.helper.layout = Layout(
            Field('description', css_class='mb-4'),
            Field('show_description', css_class='mb-4'),
        )