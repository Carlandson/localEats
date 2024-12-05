import { getCookie } from '../utils/cookies.js';
import { displayError } from '../utils/errors.js';
import { updatePreview } from '../utils/previewUpdates.js';
import { debounce } from '../utils/debounce.js';
import { updateHeroText } from './textHandlers.js';

export function initializeColorHandlers(context) {
    // Initialize brand color pickers (Global Settings)
    const brandColorPickers = document.querySelectorAll('.color-picker[data-color-type]');
    brandColorPickers.forEach(picker => {
        picker.addEventListener('input', debounce(async function() {
            try {
                const colorType = this.dataset.colorType;
                await handleBrandColorChange(colorType, this.value, context);
            } catch (error) {
                console.error('Error updating brand color:', error);
                displayError('Failed to update brand color');
            }
        }, 100));
    });

    // Initialize hero text color pickers (from banner_text_settings.html)
    const heroColorInputs = [
        'hero_heading_color', 
        'hero_subheading_color',
        'hero_banner_2_heading_color',
        'hero_banner_2_subheading_color',
        'hero_banner_3_heading_color',
        'hero_banner_3_subheading_color'
    ];
    
    heroColorInputs.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('input', debounce(async function() {
                try {
                    const field = id.replace(/-/g, '_');
                    await updateHeroText(field, this.value, context);
                } catch (error) {
                    console.error(`Error updating ${id}:`, error);
                    displayError(`Failed to update ${id.replace(/-/g, ' ')}`);
                }
            }, 100));
        }
    });
}

async function handleBrandColorChange(colorType, value, context) {
    try {
        const response = await fetch(`/${context.business_subdirectory}/update-brand-colors/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                color_type: colorType,
                color_value: value
            })
        });

        if (!response.ok) {
            throw new Error('Failed to update brand color');
        }

        const data = await response.json();
        if (data.success) {
            await updatePreview(context.pageSelector.value, context);
        } else {
            throw new Error(data.error || 'Update failed');
        }
    } catch (error) {
        console.error('Error:', error);
        displayError('Failed to update brand color: ' + error.message);
        throw error;
    }
}