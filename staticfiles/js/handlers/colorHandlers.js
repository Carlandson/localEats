import { debounce } from '../utils/debounce.js';
import { getCookie } from '../utils/cookies.js';
import { displayError } from '../utils/errors.js';
import { updatePreview } from '../utils/previewUpdates.js';

export function initializeColorPickers(context) {
    const brandColorPickers = document.querySelectorAll('.color-picker');
    
    brandColorPickers.forEach(picker => {
        picker.addEventListener('input', debounce(async function() {
            await handleColorChange(this, context);  // Pass entire context
        }, 100));
    });
}

export async function handleColorChange(picker, context) {  // Receive entire context
    const colorType = picker.dataset.colorType;
    const colorValue = picker.value;
    
    console.log('Updating brand color:', colorType, colorValue);
    
    try {
        const response = await fetch(`/${context.business_subdirectory}/update-brand-colors/`, {
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
            await updatePreview(context.pageSelector.value);
        }
    } catch (error) {
        console.error('Error updating brand color:', error);
        displayError('Failed to update brand color');
    }
}

function getColorElements() {
    return {
        heroTextColor: document.getElementById('hero-text-color'),
        heroSubtextColor: document.getElementById('hero-subtext-color')
    };
}

export function initializeColorHandlers(context) {
    const colorInputs = ['hero-text-color', 'hero-subtext-color'];
    
    colorInputs.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('input', debounce(async function() {
                try {
                    await updateHeroText(this.id, this.value, context);
                } catch (error) {
                    console.error(`Error updating ${id}:`, error);
                    displayError(`Failed to update ${id.replace(/-/g, ' ')}`);
                }
            }, 100));
        } else {
            console.warn(`Color input element not found: ${id}`);
        }
    });
}