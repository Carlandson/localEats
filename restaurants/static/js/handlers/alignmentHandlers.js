import { updateHeroText } from './textHandlers.js';
import { displayError } from '../utils/errors.js';

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
                    await updateHeroText(fieldName, this.value, context);
                } catch (error) {
                    console.error(`Error updating ${fieldName}:`, error);
                    displayError('Failed to update text alignment');
                }
            });
        });
    };

    // Set up handlers for each banner
    if (elements.heroAlignmentRadios.length > 0) {
        setupAlignmentHandler(elements.heroAlignmentRadios, 'text_align');
    }

    if (elements.banner2AlignmentRadios.length > 0) {
        setupAlignmentHandler(elements.banner2AlignmentRadios, 'hero_banner_2_text_align');
    }

    if (elements.banner3AlignmentRadios.length > 0) {
        setupAlignmentHandler(elements.banner3AlignmentRadios, 'hero_banner_3_text_align');
    }
}