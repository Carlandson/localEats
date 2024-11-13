document.addEventListener('DOMContentLoaded', function() {
    // Core initialization
    const kitchen = JSON.parse(document.getElementById('kitchen').textContent);
    const navStyle = JSON.parse(document.getElementById('nav_style').textContent);
    const restaurant_details = {
        navigation_style: navStyle
    };
    const pageSelector = document.getElementById('page-selector');
    // Image upload elements
    const uploadButton = document.getElementById('upload-hero-button');
    const fileInput = document.getElementById('hero-image-upload');
    const removeButton = document.getElementById('remove-hero-image');

    // Initialize event listeners
    if (pageSelector) {
        pageSelector.addEventListener('change', function() {
            loadPageData(this.value);
        });
    }

    // Hero Layout Radio Buttons
    document.querySelectorAll('input[name="hero_layout"]').forEach(radio => {
        radio.addEventListener('change', function() {
            updateHeroText('layout', this.value);
        });
    });

    // Text Input Fields
    const textInputs = [
        'hero-heading',
        'hero-subheading',
        'hero-button-text',
        'hero-button-link'
    ];

    textInputs.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('input', debounce(function() {
                updateHeroText(this.id, this.value);
            }, 500));
        }
    });

    // Text Alignment Handler
    document.querySelectorAll('input[name="hero-text-align"]').forEach(radio => {
        radio.addEventListener('change', function() {
            updateHeroText('text-align', this.value);
        });
    });

    // Color Pickers
    const colorInputs = ['hero-text-color', 'hero-subtext-color'];
    colorInputs.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('input', debounce(function() {
                updateHeroText(this.id, this.value);
            }, 100));
        }
    });

    // Global Component Selectors
    document.querySelectorAll('.component-selector').forEach(selector => {
        selector.addEventListener('change', function() {
            updateGlobalComponent(this.dataset.component, this.value);
        });
    });

    // Image Upload Handlers
    if (uploadButton && fileInput) {
        uploadButton.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', handleImageUpload);
    }

    if (removeButton) {
        removeButton.addEventListener('click', removeHeroImage);
    }

    // Core Functions
    async function loadPageData(pageType) {
        try {
            const response = await fetch(`/${kitchen}/get-page-data/${pageType}/`);
            if (!response.ok) throw new Error('Failed to load page data');
            
            const data = await response.json();
            
            // Update editor values
            updateFormValues(data);
            
            // Update preview
            updatePreview(pageType);
            
        } catch (error) {
            console.error('Error loading page data:', error);
            displayError('Failed to load page data');
        }
    }

    function updateFormValues(data) {
        // Update text inputs
        const textFields = {
            'hero-heading': data.hero_heading || '',
            'hero-subheading': data.hero_subheading || '',
            'hero-button-text': data.hero_button_text || '',
            'hero-button-link': data.hero_button_link || ''
        };

        Object.entries(textFields).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) element.value = value;
        });

        // Update radio buttons
        const layoutRadio = document.querySelector(`input[name="hero_layout"][value="${data.hero_layout}"]`);
        if (layoutRadio) layoutRadio.checked = true;

        // Update text alignment
        const alignRadio = document.querySelector(`input[name="hero-text-align"][value="${data.hero_text_align || 'left'}"]`);
        if (alignRadio) alignRadio.checked = true;

        // Update colors
        const colorInputs = {
            'hero-text-color': data.hero_text_color || '#000000',
            'hero-subtext-color': data.hero_subtext_color || '#6B7280'
        };

        Object.entries(colorInputs).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) element.value = value;
        });
    }

    async function updateHeroText(field, value) {
        try {
            const response = await fetch(`/${kitchen}/update-hero/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({
                    field: field.replace('hero-', ''),
                    value: value,
                    page_type: pageSelector.value
                })
            });

            if (!response.ok) throw new Error('Failed to update');
            
            const data = await response.json();
            if (data.success) {
                updatePreview(pageSelector.value);
            } else {
                throw new Error(data.error || 'Update failed');
            }
        } catch (error) {
            console.error('Error:', error);
            displayError('Failed to update: ' + error.message);
        }
    }

    async function updatePreview(pageType) {
        try {
            // First, get the navigation preview
            const navResponse = await fetch(`/${kitchen}/preview-component/navigation/top-nav/${restaurant_details.navigation_style}/`);
            if (!navResponse.ok) throw new Error('Failed to load navigation preview');
            const navHtml = await navResponse.text();
            
            // Then get the page content preview
            const pageResponse = await fetch(`/${kitchen}/preview-page/${pageType}/`);
            if (!pageResponse.ok) throw new Error('Failed to load page preview');
            const pageHtml = await pageResponse.text();
            
            // Update the preview container
            const navigationPreview = document.getElementById('navigation-preview');
            const pageContentPreview = document.getElementById('page-content-preview');
            
            if (navigationPreview) navigationPreview.innerHTML = navHtml;
            if (pageContentPreview) pageContentPreview.innerHTML = pageHtml;
            
        } catch (error) {
            console.error('Error updating preview:', error);
            displayError('Failed to update preview');
        }
    }

    async function handleImageUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('hero_image', file);
        formData.append('page_type', pageSelector.value);

        uploadButton.textContent = 'Uploading...';
        uploadButton.disabled = true;

        try {
            const response = await fetch(`/${kitchen}/upload-hero-image/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: formData
            });

            const data = await response.json();
            if (data.success) {
                updatePreview(pageSelector.value);
            } else {
                throw new Error(data.error || 'Upload failed');
            }
        } catch (error) {
            console.error('Error:', error);
            displayError('Failed to upload image: ' + error.message);
        } finally {
            uploadButton.textContent = 'Upload Image';
            uploadButton.disabled = false;
            fileInput.value = '';
        }
    }

    async function removeHeroImage() {
        if (!confirm('Are you sure you want to remove the hero image?')) return;

        removeButton.disabled = true;

        try {
            const response = await fetch(`/${kitchen}/remove-hero-image/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    page_type: pageSelector.value
                })
            });

            const data = await response.json();
            if (data.success) {
                updatePreview(pageSelector.value);
            } else {
                throw new Error(data.error || 'Remove failed');
            }
        } catch (error) {
            console.error('Error:', error);
            displayError('Failed to remove image: ' + error.message);
        } finally {
            removeButton.disabled = false;
        }
    }

    async function updateGlobalComponent(component, style) {
        try {
            const response = await fetch(`/${kitchen}/update-global-component/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({
                    component: component,
                    style: style
                })
            });

            if (!response.ok) throw new Error('Failed to update component');
            
            const data = await response.json();
            if (data.success) {
                updatePreview(pageSelector.value);
            } else {
                throw new Error(data.error || 'Update failed');
            }
        } catch (error) {
            console.error('Error:', error);
            displayError('Failed to update component: ' + error.message);
        }
    }

    function displayError(message) {
        // Implement your error display logic here
        console.error(message);
        // Example: Show a toast notification
        alert(message);
    }

    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func.apply(this, args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Initialize the first page
    loadPageData(pageSelector.value);
});