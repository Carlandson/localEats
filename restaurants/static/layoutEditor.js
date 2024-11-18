
document.addEventListener('DOMContentLoaded', function() {
    // Core initialization
    // Text Input Fields with Show/Hide Dependency
    const headingInput = document.getElementById('hero-heading');
    const subheadingInput = document.getElementById('hero-subheading');
    const showHeadingCheckbox = document.getElementById('show-hero-heading');
    const showSubheadingCheckbox = document.getElementById('show-hero-subheading');
    const business_subdirectory = JSON.parse(document.getElementById('business').textContent);
    console.log('Business subdirectory:', business_subdirectory);
    const navStyle = JSON.parse(document.getElementById('nav_style').textContent);
    const business_details = {
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
        radio.addEventListener('change', async function() {
            try {
                console.log('Updating hero layout to:', this.value);
                await updateGlobalComponent('hero_layout', this.value);
                console.log('Hero layout updated successfully');
            } catch (error) {
                console.error('Error updating hero layout:', error);
                displayError('Failed to update hero layout');
            }
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
            console.log('Text align changed to:', this.value);
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
        selector.addEventListener('change', async function() {
            const component = this.dataset.component;
            const value = this.value;
            console.log(`Updating ${component} to ${value}`);
            
            try {
                await updateGlobalComponent(component, value);
                // Force preview refresh after component update
                await updatePreview(pageSelector.value);
            } catch (error) {
                console.error(`Error updating ${component}:`, error);
                displayError(`Failed to update ${component}`);
            }
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
    // Heading Input Handler
    if (headingInput) {
        headingInput.addEventListener('input', debounce(function() {
            if (showHeadingCheckbox && showHeadingCheckbox.checked) {
                updateHeroText(this.id, this.value);
            } else {
                console.log('Heading update skipped - heading is hidden');
            }
        }, 500));
    }
    // Subheading Input Handler
    if (subheadingInput) {
        subheadingInput.addEventListener('input', debounce(function() {
            if (showSubheadingCheckbox && showSubheadingCheckbox.checked) {
                updateHeroText(this.id, this.value);
            } else {
                console.log('Subheading update skipped - subheading is hidden');
            }
        }, 500));
    }
    // Show/Hide Toggle Handlers
    if (showHeadingCheckbox) {
        showHeadingCheckbox.addEventListener('change', async function() {
            await updateHeroText('show-hero-heading', this.checked);
            if (this.checked && headingInput && headingInput.value) {
                // Update heading text if checkbox is checked and there's a value
                await updateHeroText('hero-heading', headingInput.value);
            }
        });
    }

    if (showSubheadingCheckbox) {
        showSubheadingCheckbox.addEventListener('change', async function() {
            await updateHeroText('show-hero-subheading', this.checked);
            if (this.checked && subheadingInput && subheadingInput.value) {
                // Update subheading text if checkbox is checked and there's a value
                await updateHeroText('hero-subheading', subheadingInput.value);
            }
        });
    }
    // Brand Color Pickers
    const brandColorPickers = document.querySelectorAll('.color-picker');
    brandColorPickers.forEach(picker => {
        picker.addEventListener('input', debounce(async function() {
            const colorType = this.dataset.colorType;
            const colorValue = this.value;
            
            try {
                const response = await fetch(`/${business_subdirectory}/update-brand-colors/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: JSON.stringify({
                        color_type: colorType,
                        color_value: colorValue
                    })
                });

                if (!response.ok) {
                    throw new Error('Failed to update brand color');
                }

                const data = await response.json();
                if (data.success) {
                    // Update navigation color immediately
                    // Update preview to show new colors
                    await updatePreview(pageSelector.value);
                }
            } catch (error) {
                console.error('Error updating brand color:', error);
                displayError('Failed to update brand color');
            }
        }, 100));
    });
    // Core Functions
    async function loadPageData(pageType) {
        try {
            const response = await fetch(`/${business_subdirectory}/get-page-data/${pageType}/`);
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
        if (showHeadingCheckbox) {
            showHeadingCheckbox.checked = data.show_hero_heading || false;
        }
        if (showSubheadingCheckbox) {
            showSubheadingCheckbox.checked = data.show_hero_subheading || false;
        }
    }

    async function updateHeroText(field, value) {
        console.log(`Attempting to update ${field} to:`, value);
        try {
            console.log(`Attempting to update ${field} to:`, value);
            const response = await fetch(`/${business_subdirectory}/update-hero/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({
                    field: field,
                    value: value,
                    page_type: pageSelector.value
                })
            });
    
            if (!response.ok) {
                const errorData = await response.json();
                console.error('Update failed:', errorData);
                throw new Error(errorData.error || 'Failed to update text');
            }
    
            const data = await response.json();
            console.log('Update response:', data);
            if (data.success) {
                await updatePreview(pageSelector.value);
            } else {
                throw new Error(data.error || 'Update failed');
            }
        } catch (error) {
            console.error('Error:', error);
            displayError('Failed to update text: ' + error.message);
        }
    }
    async function updatePreview(pageType) {
        try {
            console.log('Updating preview for page:', pageType);
            const timestamp = new Date().getTime();
            const response = await fetch(`/${business_subdirectory}/page-content/${pageType}/?t=${timestamp}`, {
                headers: {
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                }
            });
            
            if (!response.ok) throw new Error('Failed to load page');
            const html = await response.text();
            
            // Update the preview container
            const previewContainer = document.getElementById('page-content-preview');
            if (previewContainer) {
                previewContainer.innerHTML = html;
                console.log('Preview updated successfully');
            } else {
                console.error('Preview container not found');
                throw new Error('Preview container not found');
            }
        } catch (error) {
            console.error('Error updating preview:', error);
            displayError('Failed to update preview: ' + error.message);
        }
    }

    function createHeroImageHTML(imageUrl) {
        return `
            <div class="relative group">
                <img src="${imageUrl}" 
                     alt="Hero image" 
                     class="w-full h-40 object-cover rounded-lg">
                <button type="button"
                        id="remove-hero-image"
                        class="absolute top-2 right-2 p-2 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors"
                        title="Remove image">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                </button>
            </div>
        `;
    }

async function handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const uploadButton = document.getElementById('upload-hero-button');
    const fileInput = document.getElementById('hero-image-upload');
    const formData = new FormData();
    formData.append('hero_image', file);
    formData.append('page_type', pageSelector.value);

    uploadButton.textContent = 'Uploading...';
    uploadButton.disabled = true;

    try {
        console.log('Uploading image...');
        const response = await fetch(`/${business_subdirectory}/upload-hero-image/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: formData
        });

        const data = await response.json();
        console.log('Upload response:', data);

        if (data.success) {
            console.log('Image uploaded successfully:', data.image_url);
            
            // Find the existing image div or create a new one
            let imageDiv = document.querySelector('.relative.group');
            if (imageDiv) {
                // Replace existing image div
                imageDiv.outerHTML = createHeroImageHTML(data.image_url);
            } else {
                // Create new image div
                const uploadContainer = uploadButton.parentElement;
                uploadContainer.insertAdjacentHTML('beforeend', createHeroImageHTML(data.image_url));
            }
            
            // Update upload button text
            uploadButton.textContent = 'Replace Image';
            
            // Attach event listener to the new remove button
            const newRemoveButton = document.getElementById('remove-hero-image');
            if (newRemoveButton) {
                console.log('Attaching remove event listener to new button');
                newRemoveButton.addEventListener('click', async (e) => {
                    e.preventDefault();
                    await removeHeroImage();
                });
            }
            
            // Update preview
            console.log('Updating preview...');
            await updatePreview(pageSelector.value);
            console.log('Preview updated successfully');
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
    
        const removeButton = document.getElementById('remove-hero-image');
        const uploadButton = document.getElementById('upload-hero-button');
        
        if (!removeButton) {
            console.error('Remove button not found');
            return;
        }
    
        removeButton.disabled = true;
    
        try {
            console.log('Removing hero image for page:', pageSelector.value);
            const response = await fetch(`/${business_subdirectory}/remove-hero-image/`, {
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
            console.log('Remove response:', data);
    
            if (data.success) {
                console.log('Image removed successfully');
                
                // Find and remove the image container div
                const imageDiv = removeButton.closest('.relative.group');
                if (imageDiv) {
                    console.log('Removing image div from DOM');
                    imageDiv.remove();
                } else {
                    console.log('Image div not found');
                }
                
                // Update upload button text
                if (uploadButton) {
                    uploadButton.textContent = 'Upload Image';
                }
                
                // Update preview
                await updatePreview(pageSelector.value);
            } else {
                throw new Error(data.error || 'Remove failed');
            }
        } catch (error) {
            console.error('Error removing image:', error);
            displayError('Failed to remove image: ' + error.message);
        } finally {
            removeButton.disabled = false;
        }
    }

    async function updateGlobalComponent(component, style) {
        try {
            console.log('Sending update request:', { component, style });
            const response = await fetch(`/${business_subdirectory}/update-global-component/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({
                    component: component,
                    style: style,
                    page_type: pageSelector.value
                })
            });
    
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to update component');
            }
            
            const data = await response.json();
            console.log('Update response:', data);
            
            if (data.success) {
                // Update preview after successful component change
                await updatePreview(pageSelector.value);
                return true;
            } else {
                throw new Error(data.error || 'Update failed');
            }
        } catch (error) {
            console.error('Error:', error);
            displayError('Failed to update component: ' + error.message);
            throw error;
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