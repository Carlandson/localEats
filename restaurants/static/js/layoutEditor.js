import { displayError } from './utils/errors.js';
import { debounce } from './utils/debounce.js';
import { getCookie } from './utils/cookies.js';
import { createHeroImageHTML, createUploadPlaceholderHTML } from './utils/placeholders.js';
import { initializeImageUploads, removeHeroImage } from './handlers/imageHandlers.js';
import { initializeTextInputs } from './handlers/textHandlers.js';
import { handleBannerSliderVisibility, reinitializeSlider } from './components/heroComponents.js';
import { initializeColorHandlers } from './handlers/colorHandlers.js';
import { updatePreview } from './utils/previewUpdates.js';
import { initializeFontHandlers } from './handlers/fontHandlers.js';
import { initializeLayoutHandlers } from './handlers/layoutHandlers.js';
import { initializeAlignmentHandlers } from './handlers/alignmentHandlers.js';

function initializeEditor() {
    try {
        // Get required elements
        const businessElement = document.getElementById('business');
        const pageSelectorElement = document.getElementById('page-selector');


        if (!businessElement || !pageSelectorElement) {
            throw new Error('Required elements not found');
        }

        // Create context object
        const context = {
            business_subdirectory: JSON.parse(businessElement.textContent),
            pageSelector: pageSelectorElement
        };

        console.log('Initializing editor with context:', context);

        // Initialize all handlers
        try {
            initializeLayoutHandlers(context);
            initializeColorHandlers(context);
            initializeImageUploads(context);
            initializeTextInputs(context);
            initializeFontHandlers(context);
            initializeAlignmentHandlers(context);

        } catch (handlerError) {
            console.error('Error initializing handlers:', handlerError);
            displayError('Failed to initialize editor components');
            throw handlerError;
        }

        // Initialize page data
        loadPageData(context.pageSelector.value, context);

        // Add page selector change listener
        context.pageSelector.addEventListener('change', function() {
            loadPageData(this.value, context);
        });

        return context;
    } catch (error) {
        console.error('Error in editor initialization:', error);
        displayError('Failed to initialize editor');
        throw error;
    }
}

async function loadPageData(pageType, context) {
    try {
        const response = await fetch(`/${context.business_subdirectory}/get-page-data/${pageType}/`);
        if (!response.ok) throw new Error('Failed to load page data');
        
        const data = await response.json();
        updateFormValues(data);
        await updatePreview(pageType, context);
        
        // Initialize slider after preview is updated
        if (data.hero_layout === 'banner-slider') {
            reinitializeSlider();
        }
        
    } catch (error) {
        console.error('Error loading page data:', error);
        displayError('Failed to load page data');
    }
}

function updateFormValues(data) {
    try {
        // Handle banner slider visibility
        if (data.hero_layout === 'banner-slider') {
            handleBannerSliderVisibility('banner-slider');
            reinitializeSlider();
        }

        // Update text fields
        const textFields = {
            'hero_heading': data.hero_heading || '',
            'hero_subheading': data.hero_subheading || '',
            'hero_button_text': data.hero_button_text || '',
            'hero_button_link': data.hero_button_link || ''
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
        if (data.hero_layout === 'banner-slider') {
            handleBannerSliderVisibility('banner-slider');
        }

        Object.entries(colorInputs).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) element.value = value;
        });
    } catch (error) {
        console.error('Error updating form values:', error);
        displayError('Failed to update form values');
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    try {
        initializeEditor();
        console.log('Editor initialized successfully');
    } catch (error) {
        console.error('Failed to initialize editor:', error);
        displayError('Editor initialization failed');
    }
});