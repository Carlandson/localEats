import { displayError } from './utils/errors.js';
import { createHeroImageHTML, createUploadPlaceholderHTML } from './utils/placeholders.js';
import { initializeImageUploads, handleImageUpload, removeHeroImage } from './handlers/imageHandlers.js';
import { initializeTextInputs } from './handlers/textHandlers.js';
import { initializeHeroSizeHandler } from './handlers/sizeHandlers.js';
import { initializeColorHandlers } from './handlers/colorHandlers.js';
import { initializeFontHandlers } from './handlers/fontHandlers.js';
import { initializeLayoutHandlers } from './handlers/layoutHandlers.js';
import { initializeAlignmentHandlers } from './handlers/alignmentHandlers.js';
import { initializeHeroLayoutListener, initializeBannerButtonEditors } from './handlers/buttonHandlers.js';
import { initializePublishToggle } from './handlers/publishHandlers.js';
import { updatePublishState } from './handlers/publishHandlers.js';
import { smartUpdate } from './utils/previewUpdates.js';
import { reinitializeSlider, handleBannerSliderVisibility } from './components/heroComponents.js';

async function initializeEditor() {
    try {
        // Get required elements
        const editorConfig = JSON.parse(document.getElementById('editor-config').textContent);
        const pageSelectorElement = document.getElementById('page-selector');
        console.log('editorConfig', editorConfig);
        console.log('pageSelectorElement', pageSelectorElement);
        if (!editorConfig || !pageSelectorElement) {
            throw new Error('Required elements not found');
        }
        // Create context object
        const context = {
            business_subdirectory: editorConfig.business_subdirectory,
            pageSelector: pageSelectorElement,
            initialData: editorConfig
        };
        // Initialize all handlers
        try {
            await initializePageData(context);
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
            console.log('initializers set');
            // Add page change listener
            context.pageSelector.addEventListener('change', async function() {
                await loadPageData(this.value, context);
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
        const response = await smartUpdate(context, {
            fieldType: 'load_page',
            page_type: pageType,
            return_preview: true
        });
        console.log('response', response);
        console.log('response.data', response.is_published);
        if (response) {
            // Update publish state using the handler
            updatePublishState(response.is_published);
            
            handleBannerSliderVisibility(response.hero_layout);
            updateFormValues(response, context);

            // Update preview if we got preview HTML
            if (response.preview_html) {
                const previewContainer = document.getElementById('page-content-preview');
                if (previewContainer) {
                    previewContainer.innerHTML = response.preview_html;
                    reinitializeSlider();
                }
            }
        }
        
    } catch (error) {
        console.error('Error loading page data:', error);
        displayError('Failed to load page data');
        throw error;
    }
}

// Update initializePageData to use smartUpdate
async function initializePageData(context) {
    try {
        // Always set initial page to 'home' and use the initial data from context
        context.pageSelector.value = 'home';
        const data = context.initialData;
        // Update publish state and banner visibility
        updatePublishState(data.is_published);
        handleBannerSliderVisibility(data.hero_layout);
        // // Ensure images object exists (though it should already be there from edit_layout)
        // if (!data.images) {
        //     data.images = {
        //         hero_primary: { url: null },
        //         banner_2: { url: null },
        //         banner_3: { url: null }
        //     };
        // }

        // Update form values with the initial data
        updateFormValues(data, context);

        // Update preview if it exists
        const previewContainer = document.getElementById('page-content-preview');
        if (previewContainer && data.preview_html) {
            previewContainer.innerHTML = data.preview_html;
            reinitializeSlider();
        }
        
    } catch (error) {
        console.error('Error initializing page data:', error);
        displayError('Failed to initialize page data');
        throw error;
    }
}

function updateFormValues(data, context) {
    console.log('updateFormValues', data, context);
    try {
        // accordion states
        const accordionStates = {};
        document.querySelectorAll('.accordion-content').forEach(content => {
            accordionStates[content.id] = !content.classList.contains('hidden');
        });
        // Update text fields for primary hero
        const textFields = {
            // Primary hero
            'hero_heading': data.hero_heading || '',
            'hero_subheading': data.hero_subheading || '',
            'hero_button_text': data.hero_button_text || '',
            'hero_button_link': data.hero_button_link || '',
            // Banner 2
            'banner_2_heading': data.banner_2?.heading || '',
            'banner_2_subheading': data.banner_2?.subheading || '',
            'banner_2_button_text': data.banner_2?.button_text || '',
            'banner_2_button_link': data.banner_2?.button_link || '',
            // Banner 3
            'banner_3_heading': data.banner_3?.heading || '',
            'banner_3_subheading': data.banner_3?.subheading || '',
            'banner_3_button_text': data.banner_3?.button_text || '',
            'banner_3_button_link': data.banner_3?.button_link || ''
        };

        // Update checkbox states
        const checkboxFields = {
            'show_hero_heading': data.show_hero_heading ?? true,
            'show_hero_subheading': data.show_hero_subheading ?? true,
            'show_hero_button': data.show_hero_button ?? true,
            'show_banner_2_heading': data.banner_2?.show_heading ?? true,
            'show_banner_2_subheading': data.banner_2?.show_subheading ?? true,
            'show_banner_2_button': data.banner_2?.show_button ?? true,
            'show_banner_3_heading': data.banner_3?.show_heading ?? true,
            'show_banner_3_subheading': data.banner_3?.show_subheading ?? true,
            'show_banner_3_button': data.banner_3?.show_button ?? true
        };

        // Update font selectors
        const fontFields = {
            // Primary hero fonts
            'hero_heading_font': data.hero_heading_font || 'default',
            'hero_subheading_font': data.hero_subheading_font || 'default',
            // Banner 2 fonts
            'banner_2_heading_font': data.banner_2?.heading_font || 'default',
            'banner_2_subheading_font': data.banner_2?.subheading_font || 'default',
            // Banner 3 fonts
            'banner_3_heading_font': data.banner_3?.heading_font || 'default',
            'banner_3_subheading_font': data.banner_3?.subheading_font || 'default'
        };

        // Update size selectors
        const sizeFields = {
            // Primary hero sizes
            'hero_heading_size': data.hero_heading_size || 'default',
            'hero_subheading_size': data.hero_subheading_size || 'default',
            // Banner 2 sizes
            'banner_2_heading_size': data.banner_2?.heading_size || 'default',
            'banner_2_subheading_size': data.banner_2?.subheading_size || 'default',
            // Banner 3 sizes
            'banner_3_heading_size': data.banner_3?.heading_size || 'default',
            'banner_3_subheading_size': data.banner_3?.subheading_size || 'default'
        };
        // Update colors
        const colorInputs = {
            'hero_heading_color': data.hero_heading_color || '#000000',
            'hero_subheading_color': data.hero_subheading_color || '#6B7280',
            'banner_2_heading_color': data.banner_2?.heading_color || '#000000',
            'banner_2_subheading_color': data.banner_2?.subheading_color,
            'banner_3_heading_color': data.banner_3?.heading_color || '#000000',
            'banner_3_subheading_color': data.banner_3?.subheading_color || '#6B7280'
        };
       
        // Update alignments
        const alignmentFields = {
            'hero_text_align': data.hero_text_align || 'left',
            'banner_2_text_align': data.banner_2?.text_align || 'left',
            'banner_3_text_align': data.banner_3?.text_align || 'left'
        };
        // Update button styles
        const buttonStyles = {
            // Primary hero button
            'hero_button_bg_color': data.hero_button_bg_color || '#000000',
            'hero_button_text_color': data.hero_button_text_color || '#FFFFFF',
            'hero_button_border_color': data.hero_button_border_color || '#000000',
            'hero_button_hover_bg_color': data.hero_button_hover_bg_color || '#FFFFFF',
            'hero_button_hover_text_color': data.hero_button_hover_text_color || '#000000',
            'hero_button_hover_border_color': data.hero_button_hover_border_color || '#000000',
            // Banner 2 button
            'banner_2_button_bg_color': data.banner_2?.button_bg_color || '#000000',
            'banner_2_button_text_color': data.banner_2?.button_text_color || '#FFFFFF',
            'banner_2_button_border_color': data.banner_2?.button_border_color || '#000000',
            'banner_2_button_hover_bg_color': data.banner_2?.button_hover_bg_color || '#FFFFFF',
            'banner_2_button_hover_text_color': data.banner_2?.button_hover_text_color || '#000000',
            'banner_2_button_hover_border_color': data.banner_2?.button_hover_border_color || '#000000',
            // Banner 3 button
            'banner_3_button_bg_color': data.banner_3?.button_bg_color || '#000000',
            'banner_3_button_text_color': data.banner_3?.button_text_color || '#FFFFFF',
            'banner_3_button_border_color': data.banner_3?.button_border_color || '#000000',
            'banner_3_button_hover_bg_color': data.banner_3?.button_hover_bg_color || '#FFFFFF',
            'banner_3_button_hover_text_color': data.banner_3?.button_hover_text_color || '#000000',
            'banner_3_button_hover_border_color': data.banner_3?.button_hover_border_color || '#000000'
        };

        // Update button styles in the form
        Object.entries(buttonStyles).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.value = value;
            }
        });
        
        // Update all text inputs
        Object.entries(textFields).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.value = value;
            }
        });

        Object.entries(checkboxFields).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) element.checked = value;
        });

        Object.entries(fontFields).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.value = value;
            }
        });

        Object.entries(sizeFields).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.value = value;
            }
        });

        // Update radio buttons for layout and alignment
        const layoutRadio = document.querySelector(`input[name="hero_layout"][value="${data.hero_layout}"]`);
        if (layoutRadio) layoutRadio.checked = true;
        
        console.log('Alignment data:', alignmentFields);

        Object.entries(alignmentFields).forEach(([name, value]) => {
            const radio = document.querySelector(`input[name="${name}"][value="${value}"]`);
            if (radio) radio.checked = true;
        });

        Object.entries(colorInputs).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                console.log('Setting color:', id, 'to:', value);
                element.value = value;
                element.defaultValue = value; // Set default value too
                
                // Trigger change event
                const event = new Event('input', { bubbles: true });
                element.dispatchEvent(event);
            }
        });
        console.log('hero_primary', data.hero_image.url);
        // Update images (existing code)
        const imageElements = {
            'hero-image': {
                url: data.hero_image.url,
                prefix: 'hero_image',
                containerId: 'hero-image-container'  // Match the actual container ID
            },
            'banner_2': {
                url: data.banner_2.url,
                prefix: 'banner_2',
                containerId: 'banner_2-container'  // Expected container ID
            },
            'banner_3': {
                url: data.banner_3.url,
                prefix: 'banner_3',
                containerId: 'banner_3-container'  // Expected container ID
            }
        };
        console.log('imageElements', imageElements);
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
    } catch (error) {
        console.error('Failed to initialize editor:', error);
        displayError('Editor initialization failed');
    }
});