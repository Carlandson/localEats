import { getCookie } from '../utils/cookies.js';
import { displayError } from '../utils/errors.js';
import { updatePreview } from '../utils/previewUpdates.js';
import { debounce } from '../utils/debounce.js';
import { updateHeroText } from './textHandlers.js';

function initializeButtonEditor(prefix, context) {
    // Get all button-related elements
    const elements = {
        showButton: document.getElementById(`show_${prefix}_button`),
        buttonText: document.getElementById(`${prefix}_button_text`),
        buttonLink: document.getElementById(`${prefix}_button_link`),
        buttonBgColor: document.getElementById(`${prefix}_button_bg_color`),
        buttonTextColor: document.getElementById(`${prefix}_button_text_color`),
        buttonSize: document.getElementById(`${prefix}_button_size`),
        button: document.querySelector(`.${prefix}-button`)
    };
    // Initialize show/hide button checkbox
    if (elements.showButton) {
        elements.showButton.checked = elements.showButton.dataset.initialState === 'true';
        
        elements.showButton.addEventListener('change', async function() {
            // Enable/disable button-related inputs
            [elements.buttonText, elements.buttonLink, elements.buttonBgColor, 
             elements.buttonTextColor, elements.buttonSize].forEach(input => {
                if (input) input.disabled = !this.checked;
            });

            // Update show/hide state
            await updateHeroText(`show_${prefix}_button`, this.checked, context);
            
            // If showing button, update all button settings
            if (this.checked) {
                const updates = [
                    [elements.buttonText, `${prefix}_button_text`],
                    [elements.buttonLink, `${prefix}_button_link`],
                    [elements.buttonBgColor, `${prefix}_button_bg_color`],
                    [elements.buttonTextColor, `${prefix}_button_text_color`],
                    [elements.buttonSize, `${prefix}_button_size`]
                ];

                for (const [element, fieldName] of updates) {
                    if (element && element.value) {
                        await updateHeroText(fieldName, element.value, context);
                    }
                }
            }
        });
    }

    // Initialize other button inputs with debounce
    [
        [elements.buttonText, `${prefix}_button_text`],
        [elements.buttonLink, `${prefix}_button_link`],
        [elements.buttonBgColor, `${prefix}_button_bg_color`],
        [elements.buttonTextColor, `${prefix}_button_text_color`],
        [elements.buttonSize, `${prefix}_button_size`]
    ].forEach(([element, fieldName]) => {
        if (element) {
            element.addEventListener('input', debounce(async function() {
                await updateHeroText(fieldName, this.value, context);
            }, 500));
        }
    });
}

export function initializeBannerButtonEditors(context) {
    const prefixes = ['hero', 'hero_banner_2', 'hero_banner_3'];
    
    prefixes.forEach(prefix => {
        initializeButtonEditor(prefix, context);
    });
}

export function initializeHeroLayoutListener() {
    const layoutSelector = document.getElementById('hero_layout');
    if (layoutSelector) {
        layoutSelector.addEventListener('change', function() {
            handleBannerSliderVisibility(this.value);
        });
    }
}