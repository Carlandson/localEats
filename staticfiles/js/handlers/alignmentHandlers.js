import { updateHeroText } from './textHandlers.js';
import { displayError } from '../utils/errors.js';

function getAlignmentElements() {
    return {
        alignmentRadios: document.querySelectorAll('input[name="hero-text-align"]')
    };
}

export function initializeAlignmentHandlers(context) {
    const elements = getAlignmentElements();

    elements.alignmentRadios.forEach(radio => {
        radio.addEventListener('change', async function() {
            try {
                console.log('Text align changed to:', this.value);
                await updateHeroText('text-align', this.value, context);
            } catch (error) {
                console.error('Error updating text alignment:', error);
                displayError('Failed to update text alignment');
            }
        });
    });
}