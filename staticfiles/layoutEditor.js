import { debounce } from './js/utils/debounce.js';
import { displayError } from './js/utils/errors.js';
import { getCookie } from './js/utils/cookies.js';
import { 
    initializeImageUploads, 
    handleImageUpload, 
    removeHeroImage 
} from './handlers/imageHandlers.js';
import { 
    initializeTextInputs, 
    updateHeroText 
} from './handlers/textHandlers.js';
import { 
    createHeroImageHTML, 
    createUploadPlaceholderHTML 
} from './templates/placeholders.js';

document.addEventListener('DOMContentLoaded', function() {
    const headingInput = document.getElementById('hero-heading');
    const subheadingInput = document.getElementById('hero-subheading');
    const showHeadingCheckbox = document.getElementById('show-hero-heading');
    const showSubheadingCheckbox = document.getElementById('show-hero-subheading');
    console.log('Checkbox element:', showHeadingCheckbox);
    console.log('Initial state:', showHeadingCheckbox?.dataset.initialState);
    console.log('Is checked:', showHeadingCheckbox?.checked);

    if (showHeadingCheckbox) {
        showHeadingCheckbox.checked = showHeadingCheckbox.dataset.initialState === 'true';
        
        showHeadingCheckbox.addEventListener('change', async function() {
            if (headingInput) {
                headingInput.disabled = !this.checked;
            }
            await updateHeroText('show-hero-heading', this.checked);
            // If checkbox is checked and there's a value, update the heading
            if (this.checked && headingInput && headingInput.value) {
                await updateHeroText('hero-heading', headingInput.value);
            }
        });
    }

    if (showSubheadingCheckbox) {
        showSubheadingCheckbox.checked = showSubheadingCheckbox.dataset.initialState === 'true';
        
        showSubheadingCheckbox.addEventListener('change', async function() {
            if (subheadingInput) {
                subheadingInput.disabled = !this.checked;
            }
            await updateHeroText('show-hero-subheading', this.checked);
            // If checkbox is checked and there's a value, update the subheading
            if (this.checked && subheadingInput && subheadingInput.value) {
                await updateHeroText('hero-subheading', subheadingInput.value);
            }
        });
    }
    // Font and size selectors
    const heroHeadingFontSelect = document.getElementById('hero-heading-font');
    const heroSubheadingFontSelect = document.getElementById('hero-subheading-font');
    const heroHeadingSizeSelect = document.getElementById('hero-heading-size');
    const heroSubheadingSizeSelect = document.getElementById('hero-subheading-size');
    const business_subdirectory = JSON.parse(document.getElementById('business').textContent);
    console.log('Business subdirectory:', business_subdirectory);
    const navStyle = JSON.parse(document.getElementById('nav_style').textContent);
    const pageSelector = document.getElementById('page-selector');
    // Image upload elements
    const uploadButton = document.getElementById('upload-hero-button');
    const fileInput = document.getElementById('hero-image-upload');
    // Font selectors
    const mainFontSelect = document.getElementById('main-font');
    if (mainFontSelect) {
        mainFontSelect.addEventListener('change', async function() {
            try {
                await updateGlobalComponent('main_font', this.value);
                // Update the preview to show new font
                await updatePreview(pageSelector.value);
            } catch (error) {
                console.error('Error updating main font:', error);
                displayError('Failed to update main font');
            }
        });

        // Add preview on hover
        mainFontSelect.addEventListener('mouseover', function(e) {
            if (e.target.tagName === 'OPTION') {
                // Temporarily apply the font to preview it
                e.target.style.fontFamily = e.target.value;
            }
        });
    }
    if (heroHeadingFontSelect) {
        heroHeadingFontSelect.addEventListener('change', async function() {
            await updateGlobalComponent('hero_heading_font', this.value);
        });
    }

    if (heroSubheadingFontSelect) {
        heroSubheadingFontSelect.addEventListener('change', async function() {
            await updateGlobalComponent('hero_subheading_font', this.value);
        });
    }

    if (heroHeadingSizeSelect) {
        heroHeadingSizeSelect.addEventListener('change', async function() {
            await updateGlobalComponent('hero_heading_size', this.value);
        });
    }

    if (heroSubheadingSizeSelect) {
        heroSubheadingSizeSelect.addEventListener('change', async function() {
            await updateGlobalComponent('hero_subheading_size', this.value);
        });
    }

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
                // Removed duplicate updatePreview call
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

    // Brand Color Pickers
    const brandColorPickers = document.querySelectorAll('.color-picker');
    brandColorPickers.forEach(picker => {
        picker.addEventListener('input', debounce(async function() {
            const colorType = this.dataset.colorType;
            const colorValue = this.value;
            console.log('Updating brand color:', colorType, colorValue);
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

    const footerStyleSelect = document.getElementById('footer-style');
    if (footerStyleSelect) {
        footerStyleSelect.addEventListener('change', async function() {
            try {
                await updateGlobalComponent('footer_style', this.value);
                // Update preview to show new footer
                await updatePreview(pageSelector.value);
            } catch (error) {
                console.error('Error updating footer style:', error);
                displayError('Failed to update footer style');
            }
        });
    }
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
        if (data.hero_layout === 'banner-slider') {
            handleBannerSliderVisibility('banner-slider');
        }
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

    // async function updateHeroText(field, value) {
    //     console.log(`Attempting to update ${field} to:`, value);
    //     try {
    //         console.log(`Attempting to update ${field} to:`, value);
    //         const response = await fetch(`/${business_subdirectory}/update-hero/`, {
    //             method: 'POST',
    //             headers: {
    //                 'Content-Type': 'application/json',
    //                 'X-CSRFToken': getCookie('csrftoken'),
    //             },
    //             body: JSON.stringify({
    //                 field: field,
    //                 value: value,
    //                 page_type: pageSelector.value
    //             })
    //         });
    
    //         if (!response.ok) {
    //             const errorData = await response.json();
    //             console.error('Update failed:', errorData);
    //             throw new Error(errorData.error || 'Failed to update text');
    //         }
    
    //         const data = await response.json();
    //         console.log('Update response:', data);
    //         if (data.success) {
    //             await updatePreview(pageSelector.value);
    //         } else {
    //             throw new Error(data.error || 'Update failed');
    //         }
    //     } catch (error) {
    //         console.error('Error:', error);
    //         displayError('Failed to update text: ' + error.message);
    //     }
    // }
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

    // function initializeImageUploads() {
    //     ['hero-image', 'banner-2', 'banner-3'].forEach(prefix => {
    //         const uploadButton = document.getElementById(`upload-${prefix}-button`);
    //         const fileInput = document.getElementById(`${prefix}-upload`);
            
    //         if (uploadButton && fileInput) {
    //             uploadButton.addEventListener('click', () => {
    //                 if (!uploadButton.disabled) {
    //                     fileInput.click();
    //                 }
    //             });
                
    //             fileInput.addEventListener('change', handleImageUpload);
    //         }
    //     });
    //     attachRemoveListeners();
    // }

    // async function handleImageUpload(event) {
    //     const file = event.target.files[0];
    //     if (!file) return;
    
    //     // Get the prefix from the input ID
    //     const inputId = event.target.id;
    //     const prefix = inputId.replace('-upload', '');
        
    //     const uploadButton = document.getElementById(`upload-${prefix}-button`);
    //     const formData = new FormData();
    //     formData.append('image', file);
    //     formData.append('page_type', pageSelector.value);
    
    //     // Map the prefix to the correct banner type
    //     let bannerType;
    //     switch(prefix) {
    //         case 'hero-image':
    //             bannerType = 'primary';
    //             break;
    //         case 'banner-2':
    //             bannerType = 'banner_2';
    //             break;
    //         case 'banner-3':
    //             bannerType = 'banner_3';
    //             break;
    //         default:
    //             bannerType = 'primary';
    //     }
    //     formData.append('banner_type', bannerType);

    //     if (uploadButton) {
    //         uploadButton.textContent = 'Uploading...';
    //         uploadButton.disabled = true;
    //     }

    //     try {
    //         console.log('Uploading image...', prefix);
    //         const response = await fetch(`/${business_subdirectory}/upload-hero-image/`, {
    //             method: 'POST',
    //             headers: {
    //                 'X-CSRFToken': getCookie('csrftoken'),
    //             },
    //             body: formData
    //         });

    //         const data = await response.json();
    //         console.log('Upload response:', data);

    //         if (data.success) {
    //             console.log('Image uploaded successfully:', data.image_url);
                
    //             // Update the container with the new image
    //             const container = document.getElementById(`${prefix}-container`);
    //             if (container) {
    //                 // Use the createHeroImageHTML function instead of inline HTML
    //                 container.innerHTML = `
    //                     ${createHeroImageHTML(data.image_url, prefix)}
    //                     <input type="file" id="${prefix}-upload" accept="image/*" class="hidden">
    //                 `;
                    
    //                 // Reattach event listeners
    //                 initializeImageUploads();
    //                 attachRemoveListeners();
    //             }
                
    //             // Update preview
    //             await updatePreview(pageSelector.value);
    //         } else {
    //             throw new Error(data.error || 'Upload failed');
    //         }
    //     } catch (error) {
    //         console.error('Error uploading image:', error);
    //         displayError('Failed to upload image: ' + error.message);
    //     } finally {
    //         if (uploadButton) {
    //             uploadButton.textContent = 'Upload Image';
    //             uploadButton.disabled = false;
    //         }
    //     }
    // }

    function attachRemoveListeners() {
        ['hero-image', 'banner-2', 'banner-3'].forEach(prefix => {
            const removeButton = document.getElementById(`remove-${prefix}`);
            if (removeButton) {
                // Remove existing listeners first
                const newButton = removeButton.cloneNode(true);
                removeButton.parentNode.replaceChild(newButton, removeButton);
                
                // Add new listener
                newButton.addEventListener('click', function() {
                    window.removeHeroImage(prefix);
                });
            }
        });
    }
    
    function handleBannerSliderVisibility(layoutStyle) {
        const bannerSliderContainer = document.getElementById('banner-slider-images');
        if (!bannerSliderContainer) return;
    
        console.log('Handling banner slider visibility:', layoutStyle);
        
        if (layoutStyle === 'banner-slider') {
            console.log('Displaying banner slider');
            bannerSliderContainer.style.display = 'block';
            // Enable banner upload inputs and buttons
            ['banner-2', 'banner-3'].forEach(prefix => {
                const fileInput = document.getElementById(`${prefix}-upload`);
                const uploadButton = document.getElementById(`upload-${prefix}-button`);
                const container = document.getElementById(`${prefix}-container`);
                const removeButton = document.getElementById(`remove-${prefix}`);
                
                if (fileInput) fileInput.disabled = false;
                if (uploadButton) {
                    uploadButton.disabled = false;
                    uploadButton.classList.remove('opacity-50', 'cursor-not-allowed');
                }
                if (container) {
                    container.classList.remove('opacity-50');
                }
                if (removeButton) {
                    removeButton.disabled = false;
                }
            });
        } else {
            bannerSliderContainer.style.display = 'none';
            // Disable banner upload inputs and buttons
            ['banner-2', 'banner-3'].forEach(prefix => {
                const fileInput = document.getElementById(`${prefix}-upload`);
                const uploadButton = document.getElementById(`upload-${prefix}-button`);
                const container = document.getElementById(`${prefix}-container`);
                const removeButton = document.getElementById(`remove-${prefix}`);
                
                if (fileInput) fileInput.disabled = true;
                if (uploadButton) {
                    uploadButton.disabled = true;
                    uploadButton.classList.add('opacity-50', 'cursor-not-allowed');
                }
                if (container) {
                    container.classList.add('opacity-50');
                }
                if (removeButton) {
                    removeButton.disabled = true;
                }
            });
        }
    }

    async function updateGlobalComponent(component, style) {
        try {
            console.log('Sending update request:', { component, style });
                    // Handle banner slider visibility if this is a hero layout update
            if (component === 'hero_layout') {
                console.log('Updating banner slider visibility:', style);
                handleBannerSliderVisibility(style);
            }
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
    // function displayError(message) {
    //     // Implement your error display logic here
    //     console.error(message);
    //     // Example: Show a toast notification
    //     alert(message);
    // }

    // function debounce(func, wait) {
    //     let timeout;
    //     return function executedFunction(...args) {
    //         const later = () => {
    //             clearTimeout(timeout);
    //             func.apply(this, args);
    //         };
    //         clearTimeout(timeout);
    //         timeout = setTimeout(later, wait);
    //     };
    // }
    // function getCookie(name) {
    //     let cookieValue = null;
    //     if (document.cookie && document.cookie !== '') {
    //         const cookies = document.cookie.split(';');
    //         for (let i = 0; i < cookies.length; i++) {
    //             const cookie = cookies[i].trim();
    //             if (cookie.substring(0, name.length + 1) === (name + '=')) {
    //                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
    //                 break;
    //             }
    //         }
    //     }
    //     return cookieValue;
    // }
    // Initialize the first page
    initializeImageUploads();
    loadPageData(pageSelector.value);
});

// window.createHeroImageHTML = function(imageUrl, prefix, layout = 'banner-slider') {
//     const isDisabled = prefix !== 'hero-image' && layout !== 'banner-slider';
//     return `
//         <div class="relative group">
//             <img src="${imageUrl}" 
//                  alt="${prefix} image" 
//                  class="w-full h-40 object-cover rounded-lg cursor-pointer"
//                  id="${prefix}-preview">
//             <button type="button"
//                     id="remove-${prefix}"
//                     class="absolute top-2 right-2 p-2 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors"
//                     title="Remove image"
//                     >
//                 <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
//                     <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
//                 </svg>
//             </button>
//         </div>
//     `;
// };

// window.removeHeroImage = async function(prefix) {
//     if (!confirm('Are you sure you want to remove this image?')) return;

//     const removeButton = document.getElementById(`remove-${prefix}`);
//     const container = document.getElementById(`${prefix}-container`);
//     const business_subdirectory = document.getElementById('business')?.textContent?.trim().replace(/['"]/g, '');
//     const pageSelector = document.getElementById('page-selector');
    
//     if (!removeButton || !container || !business_subdirectory || !pageSelector) {
//         console.error('Required elements not found');
//         return;
//     }

//     removeButton.disabled = true;

//     try {
//         console.log('Removing image for prefix:', prefix);
//         const response = await fetch(`/${business_subdirectory}/remove-hero-image/`, {
//             method: 'POST',
//             headers: {
//                 'X-CSRFToken': getCookie('csrftoken'),
//                 'Content-Type': 'application/json',
//             },
//             body: JSON.stringify({
//                 page_type: pageSelector.value,
//                 banner_type: prefix === 'hero-image' ? 'primary' : prefix.replace('banner-', '')
//             })
//         });

//         const data = await response.json();
//         console.log('Remove response:', data);

//         if (data.success) {
//             console.log('Image removed successfully');
//             container.innerHTML = createUploadPlaceholderHTML(prefix);
//             initializeImageUploads();
//             await updatePreview(pageSelector.value);
//         } else {
//             throw new Error(data.error || 'Remove failed');
//         }
//     } catch (error) {
//         console.error('Error removing image:', error);
//         alert('Failed to remove image: ' + error.message);
//     } finally {
//         if (removeButton) {
//             removeButton.disabled = false;
//         }
//     }
// };

// window.createUploadPlaceholderHTML = function(prefix) {
//     const displayText = prefix === 'hero-image' ? 'Add Primary Image' : `Add ${prefix.replace('-', ' ').replace(/^\w/, c => c.toUpperCase())}`;
//     return `
//         <div class="relative group cursor-pointer" id="${prefix}-placeholder">
//             <div class="w-full h-40 bg-gray-100 rounded-lg flex items-center justify-center border-2 border-dashed border-gray-300 hover:border-gray-400">
//                 <div class="text-center">
//                     <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
//                         <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
//                     </svg>
//                     <span class="mt-2 block text-sm font-medium text-gray-600">
//                         ${displayText}
//                     </span>
//                 </div>
//             </div>
//             <input type="file" 
//                    id="${prefix}-upload" 
//                    accept="image/*" 
//                    class="hidden">
//         </div>
//     `;
// };
