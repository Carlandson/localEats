import { displayError } from '../utils/errors.js';
import { smartUpdate } from '../utils/previewUpdates.js';
import { handleBannerSliderVisibility } from '../components/heroComponents.js';

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
            try {
                // Enable/disable button-related inputs
                [elements.buttonText, elements.buttonLink, elements.buttonBgColor, 
                 elements.buttonTextColor, elements.buttonSize].forEach(input => {
                    if (input) input.disabled = !this.checked;
                });

                // Update show/hide state
                await smartUpdate(context, {
                    fieldType: 'toggle',
                    fieldName: `show_${prefix}_button`,
                    value: this.checked,
                    previousValue: !this.checked,
                    page_type: context.pageSelector.value,
                    return_preview: true,
                    isGlobal: false
                });

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
                            await smartUpdate(context, {
                                fieldType: 'button',
                                fieldName: fieldName,
                                value: element.value,
                                previousValue: element.defaultValue,
                                page_type: context.pageSelector.value,
                                return_preview: true
                            });
                        }
                    }
                }
            } catch (error) {
                console.error('Error updating button visibility:', error);
                displayError('Failed to update button visibility');
            }
        });
    }

    // Define input types and their update strategies
    const inputConfigs = [
        // Text inputs should be debounced
        [elements.buttonText, `${prefix}_button_text`, 'text'],
        // Links should update immediately
        [elements.buttonLink, `${prefix}_button_link`, 'button'],
        // Colors should be debounced
        [elements.buttonBgColor, `${prefix}_button_bg_color`, 'color'],
        [elements.buttonTextColor, `${prefix}_button_text_color`, 'color'],
        // Size should update immediately
        [elements.buttonSize, `${prefix}_button_size`, 'button']
    ];

    inputConfigs.forEach(([element, fieldName, fieldType]) => {
        if (element) {
            element.addEventListener('input', async function() {
                try {
                    await smartUpdate(context, {
                        fieldType: fieldType,
                        fieldName: fieldName,
                        value: this.value,
                        previousValue: this.defaultValue,
                        page_type: context.pageSelector.value,
                        return_preview: true
                    });
                    // Update the defaultValue for future changes
                    this.defaultValue = this.value;
                } catch (error) {
                    console.error(`Error updating ${fieldName}:`, error);
                    displayError(`Failed to update button ${fieldName.split('_').pop()}`);
                }
            });
        }
    });
}

export function initializeBannerButtonEditors(context) {
    const prefixes = ['hero', 'banner_2', 'banner_3'];
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