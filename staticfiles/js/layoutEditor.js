import { displayError } from './utils/errors.js';
import { debounce } from './utils/debounce.js';
import { getCookie } from './utils/cookies.js';
import { createHeroImageHTML, createUploadPlaceholderHTML } from './utils/placeholders.js';
import { initializeImageUploads, removeHeroImage } from './handlers/imageHandlers.js';
import { initializeTextInputs, updateHeroText } from './handlers/textHandlers.js';
import { updateGlobalComponent } from './components/globalComponents.js';
import { handleBannerSliderVisibility } from './components/heroComponents.js';
import { slider } from './components/slider.js';
import { initializeColorHandlers } from './handlers/colorHandlers.js';
import { handleColorChange } from './handlers/colorHandlers.js';
import { updatePreview } from './utils/previewUpdates.js';
import { initializeFontHandlers } from './handlers/fontHandlers.js';
import { initializeLayoutHandlers } from './handlers/layoutHandlers.js';
import { initializeAlignmentHandlers } from './handlers/alignmentHandlers.js';
console.log('Layout Editor loaded');
document.addEventListener('DOMContentLoaded', function() {
    const context = {
        business_subdirectory: JSON.parse(document.getElementById('business').textContent),
        pageSelector: document.getElementById('page-selector')
    }
    console.log('Initialized with context:', context);
    initializeLayoutHandlers(context);
    initializeColorPickers(context);
    initializeImageUploads(context);
    initializeTextInputs(context);
    initializeFontHandlers(context);
    initializeAlignmentHandlers(context);
    const pageSelector = document.getElementById('page-selector');

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
    updateHeroText(field, value);
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
    initializeImageUploads();
    loadPageData(pageSelector.value);
});

