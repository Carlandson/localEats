import { displayError } from './utils/errors.js';
import { createHeroImageHTML, createUploadPlaceholderHTML } from './utils/placeholders.js';
import { initializeImageUploads, handleImageUpload, removeHeroImage } from './handlers/imageHandlers.js';
import { initializeTextInputs } from './handlers/textHandlers.js';
import { initializeHeroSizeHandler } from './handlers/sizeHandlers.js';
import { initializeColorHandlers } from './handlers/colorHandlers.js';
import { updatePreview } from './utils/previewUpdates.js';
import { initializeFontHandlers } from './handlers/fontHandlers.js';
import { initializeLayoutHandlers } from './handlers/layoutHandlers.js';
import { initializeAlignmentHandlers } from './handlers/alignmentHandlers.js';
import { initializeHeroLayoutListener, initializeBannerButtonEditors } from './handlers/buttonHandlers.js';
import { handleBannerSliderVisibility } from './components/heroComponents.js';
import { initializePublishToggle } from './handlers/publishHandlers.js';
import { updatePublishState } from './handlers/publishHandlers.js';

async function initializeEditor() {
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
            await loadPageData(context.pageSelector.value, context);
            initializePublishToggle(context);
            initializeHeroLayoutListener();
            initializeBannerButtonEditors(context);
            initializeLayoutHandlers(context);
            initializeColorHandlers(context);
            initializeImageUploads(context);
            initializeTextInputs(context);
            initializeFontHandlers(context);
            initializeAlignmentHandlers(context);
            initializeHeroSizeHandler(context);
            context.pageSelector.addEventListener('change', function() {
                loadPageData(this.value, context);
            });

        } catch (handlerError) {
            console.error('Error initializing handlers:', handlerError);
            displayError('Failed to initialize editor components');
            throw handlerError;
        }

        return context;
    } catch (error) {
        console.error('Error in editor initialization:', error);
        displayError('Failed to initialize editor');
        throw error;
    }
}

function initializeAccordions() {
    document.querySelectorAll('.accordion-trigger').forEach(trigger => {
        // Remove any existing event listeners
        const newTrigger = trigger.cloneNode(true);
        trigger.parentNode.replaceChild(newTrigger, trigger);
        
        newTrigger.addEventListener('click', () => {
            const target = document.getElementById(newTrigger.dataset.target);
            const arrow = newTrigger.querySelector('svg');
            
            // Toggle panel visibility
            target.classList.toggle('hidden');
            
            // Update trigger styles and arrow rotation
            if (target.classList.contains('hidden')) {
                newTrigger.classList.remove('bg-gray-100', 'hover:bg-gray-400');
                newTrigger.classList.add('bg-white', 'hover:bg-gray-50');
                arrow.classList.remove('rotate-90');
            } else {
                newTrigger.classList.remove('bg-white', 'hover:bg-gray-50');
                newTrigger.classList.add('bg-gray-100', 'hover:bg-gray-400');
                arrow.classList.add('rotate-90');
            }
        });
    });
}

function wrapInAccordion(title, content, isOpen = false) {
    // Generate consistent ID based on title
    const accordionId = title.toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/(^-|-$)/g, '');

    return `
        <div class="border rounded-lg mb-4">
            <button class="accordion-trigger w-full flex justify-between items-center p-4 ${isOpen ? 'bg-gray-100 hover:bg-gray-400' : 'bg-white hover:bg-gray-50'} rounded-t-lg" 
                    data-target="${accordionId}-content">
                <h2 class="text-lg font-bold">${title}</h2>
                <svg class="w-5 h-5 transition-transform ${isOpen ? 'rotate-90' : ''}" 
                     xmlns="http://www.w3.org/2000/svg" 
                     fill="none" 
                     viewBox="0 0 24 24" 
                     stroke="currentColor">
                    <path stroke-linecap="round" 
                          stroke-linejoin="round" 
                          stroke-width="2" 
                          d="M9 5l7 7-7 7" />
                </svg>
            </button>
            <div id="${accordionId}-content" 
                 class="accordion-content p-4 ${isOpen ? '' : 'hidden'}"
                 data-section="${accordionId}">
                ${content}
            </div>
        </div>
    `;
}

async function loadPageData(pageType, context) {
    try {
        const response = await fetch(`/${context.business_subdirectory}/get-page-data/${pageType}/`);
        if (!response.ok) throw new Error('Failed to load page data');
        const data = await response.json();
        
        // Update publish state using the handler
        updatePublishState(data.is_published);
        
        console.log("Published state of ", pageType, " is: ", data.is_published);
        handleBannerSliderVisibility(data.hero_layout);
        updateFormValues(data, context);
        await updatePreview(pageType, context, true);
        
    } catch (error) {
        console.error('Error loading page data:', error);
        displayError('Failed to load page data');
    }
}

function updateFormValues(data, context) {
    try {
        const accordionStates = {};
        document.querySelectorAll('.accordion-content').forEach(content => {
            accordionStates[content.id] = !content.classList.contains('hidden');
        });


        // Update text fields for primary hero
        const textFields = {
            'hero_heading': data.hero_heading || '',
            'hero_subheading': data.hero_subheading || '',
            'hero_button_text': data.hero_button_text || '',
            'hero_button_link': data.hero_button_link || '',
            // Banner 2 text fields
            'hero_banner_2_heading': data.hero_banner_2.heading || '',
            'hero_banner_2_subheading': data.hero_banner_2.subheading || '',
            'hero_banner_2_button_text': data.hero_banner_2.button_text || '',
            'hero_banner_2_button_link': data.hero_banner_2.button_link || '',
            // Banner 3 text fields
            'hero_banner_3_heading': data.hero_banner_3.heading || '',
            'hero_banner_3_subheading': data.hero_banner_3.subheading || '',
            'hero_banner_3_button_text': data.hero_banner_3.button_text || '',
            'hero_banner_3_button_link': data.hero_banner_3.button_link || ''
        };
        // Update all text inputs
        Object.entries(textFields).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) element.value = value;
        });

        // Update all checkbox states
        const checkboxFields = {
            'show_hero_heading': data.show_hero_heading,
            'show_hero_subheading': data.show_hero_subheading,
            'show_hero_button': data.show_hero_button,
            'show_banner_2_heading': data.hero_banner_2.show_heading,
            'show_banner_2_subheading': data.hero_banner_2.show_subheading,
            'show_banner_2_button': data.hero_banner_2.show_button,
            'show_banner_3_heading': data.hero_banner_3.show_heading,
            'show_banner_3_subheading': data.hero_banner_3.show_subheading,
            'show_banner_3_button': data.hero_banner_3.show_button
        };

        Object.entries(checkboxFields).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) element.checked = value;
        });

        // Update all font selectors
        const fontFields = {
            'hero_heading_font': data.hero_heading_font,
            'hero_subheading_font': data.hero_subheading_font,
            'hero_banner_2_heading_font': data.hero_banner_2.heading_font,
            'hero_banner_2_subheading_font': data.hero_banner_2.subheading_font,
            'hero_banner_3_heading_font': data.hero_banner_3.heading_font,
            'hero_banner_3_subheading_font': data.hero_banner_3.subheading_font
        };

        Object.entries(fontFields).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) element.value = value;
        });

        // Update all size selectors
        const sizeFields = {
            'hero_heading_size': data.hero_heading_size,
            'hero_subheading_size': data.hero_subheading_size,
            'hero_banner_2_heading_size': data.hero_banner_2.heading_size,
            'hero_banner_2_subheading_size': data.hero_banner_2.subheading_size,
            'hero_banner_3_heading_size': data.hero_banner_3.heading_size,
            'hero_banner_3_subheading_size': data.hero_banner_3.subheading_size
        };

        Object.entries(sizeFields).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) element.value = value;
        });

        // Update radio buttons for layout and alignment
        const layoutRadio = document.querySelector(`input[name="hero_layout"][value="${data.hero_layout}"]`);
        if (layoutRadio) layoutRadio.checked = true;

        // Update text alignments
        const alignmentFields = {
            'hero_text_align': data.hero_text_align || 'left',
            'hero_banner_2_text_align': data.hero_banner_2.text_align || 'left',
            'hero_banner_3_text_align': data.hero_banner_3.text_align || 'left'
        };

        Object.entries(alignmentFields).forEach(([name, value]) => {
            const radio = document.querySelector(`input[name="${name}"][value="${value}"]`);
            if (radio) radio.checked = true;
        });

        // Update colors (existing code)
        const colorInputs = {
            'hero_heading_color': data.hero_heading_color || '#000000',
            'hero_subheading_color': data.hero_subheading_color || '#6B7280',
            'hero_banner_2_heading_color': data.hero_banner_2.heading_color || '#000000',
            'hero_banner_2_subheading_color': data.hero_banner_2.subheading_color || '#6B7280',
            'hero_banner_3_heading_color': data.hero_banner_3.heading_color || '#000000',
            'hero_banner_3_subheading_color': data.hero_banner_3.subheading_color || '#6B7280'
        };

        Object.entries(colorInputs).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.value = value;
                console.log(`Setting ${id} to ${value}`);
            }
        });

        // Update images (existing code)
        const imageElements = {
            'hero-image': {
                url: data.images.hero_primary.url,
                prefix: 'hero-image',
                containerId: 'hero-image-container'  // Match the actual container ID
            },
            'hero_banner_2': {
                url: data.images.hero_banner_2.url,
                prefix: 'hero_banner_2',
                containerId: 'hero_banner_2-container'  // Expected container ID
            },
            'hero_banner_3': {
                url: data.images.hero_banner_3.url,
                prefix: 'hero_banner_3',
                containerId: 'hero_banner_3-container'  // Expected container ID
            }
        };
        const editorSections = document.querySelectorAll('.editor-section');
        editorSections.forEach(section => {
            // Skip if section is already wrapped in accordion
            if (section.closest('.accordion-trigger')) return;

            const sectionTitle = section.querySelector('h1, h2').textContent;
            const sectionContent = section.innerHTML;
            const sectionId = section.dataset.section;
            
            // Create accordion wrapper, maintaining previous state if it existed
            const wasOpen = accordionStates[`${sectionId}-content`] ?? (sectionId === 'global');
            const accordionHTML = wrapInAccordion(
                sectionTitle,
                sectionContent,
                wasOpen
            );
            
            // Replace original section with accordion
            section.outerHTML = accordionHTML;
        });

        // Reinitialize accordions
        initializeAccordions();

        Object.entries(imageElements).forEach(([id, imageData]) => {
            const { url, prefix, containerId } = imageData;
            
            // Try to find the container by ID first
            const container = document.getElementById(containerId);
            
            if (container) {
                if (url) {
                    container.innerHTML = createHeroImageHTML(url, prefix, data.hero_layout);
                    console.log(`Updated ${prefix} with image:`, url);
                    const removeButton = document.getElementById(`remove-${prefix}`);
                    if (removeButton) {
                        removeButton.addEventListener('click', () => removeHeroImage(prefix, context));
                    }
                } else {
                    // Update container with placeholder
                    container.innerHTML = createUploadPlaceholderHTML(prefix);
                    
                    // Add upload button and file input listeners
                    const uploadButton = document.getElementById(`upload-${prefix}-button`);
                    const fileInput = document.getElementById(`${prefix}-upload`);
                    
                    if (uploadButton && fileInput) {
                        uploadButton.addEventListener('click', () => {
                            if (!uploadButton.disabled) {
                                fileInput.click();
                            }
                        });

                        fileInput.addEventListener('change', async (event) => {
                            await handleImageUpload(event, context);
                        });
                    }
                }
            } else {
                console.warn(`Container not found: ${containerId}`);
            }
        });

    } catch (error) {
        console.error('Error updating form values:', error);
        displayError('Failed to update form values');
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', async function() {
    try {
        await initializeEditor();
        console.log('Editor initialized successfully');
    } catch (error) {
        console.error('Failed to initialize editor:', error);
        displayError('Editor initialization failed');
    }
});