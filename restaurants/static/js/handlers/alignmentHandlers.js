import { displayError } from '../utils/errors.js';
import { smartUpdate } from '../utils/previewUpdates.js';

function getAlignmentElements() {
    return {
        heroAlignmentRadios: document.querySelectorAll('input[name="hero_text_align"]'),
        banner2AlignmentRadios: document.querySelectorAll('input[name="hero_banner_2_text_align"]'),
        banner3AlignmentRadios: document.querySelectorAll('input[name="hero_banner_3_text_align"]')
    };
}

export function initializeAlignmentHandlers(context) {
    const elements = getAlignmentElements();
    
    // Helper function to set up alignment handlers
    const setupAlignmentHandler = (radios, fieldName) => {
        radios.forEach(radio => {
            radio.addEventListener('change', async function() {
                try {
                    console.log(`${fieldName} changed to:`, this.value);
                    
                    await smartUpdate(context, {
                        fieldType: 'alignment',
                        fieldName: fieldName,
                        value: this.value,
                        previousValue: this.dataset.previousValue || 'left', // Default to 'left' if no previous value
                        page_type: context.pageSelector.value,
                        return_preview: true,
                        isGlobal: false
                    });

                    // Update the previous value for future changes
                    this.dataset.previousValue = this.value;

                } catch (error) {
                    console.error(`Error updating ${fieldName}:`, error);
                    displayError('Failed to update text alignment');
                }
            });
        });
    };

    // Set up handlers for each banner
    if (elements.heroAlignmentRadios.length > 0) {
        setupAlignmentHandler(elements.heroAlignmentRadios, 'hero_text_align');
    }

    if (elements.banner2AlignmentRadios.length > 0) {
        setupAlignmentHandler(elements.banner2AlignmentRadios, 'banner_2_text_align');
    }

    if (elements.banner3AlignmentRadios.length > 0) {
        setupAlignmentHandler(elements.banner3AlignmentRadios, 'banner_3_text_align');
    }
}