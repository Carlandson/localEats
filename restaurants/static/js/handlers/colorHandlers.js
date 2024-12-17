import { displayError } from '../utils/errors.js';
import { smartUpdate } from '../utils/previewUpdates.js';

export function initializeColorHandlers(context) {
    // Initialize brand color pickers (Global Settings)
    const brandColorPickers = document.querySelectorAll('.color-picker[data-color-type]');
    brandColorPickers.forEach(picker => {
        picker.addEventListener('input', async function() {
            try {
                const colorType = this.dataset.colorType;  // e.g., 'primary', 'secondary'
                console.log('Updating color:', colorType, 'to:', this.value); // Debug log
                await smartUpdate(context, {
                    fieldType: 'color',
                    fieldName: colorType,  // Just send 'primary', 'secondary', etc.
                    value: this.value,
                    previousValue: this.defaultValue,
                    page_type: context.pageSelector.value,
                    isGlobal: true,  // Brand colors are global
                    return_preview: true
                });
                this.defaultValue = this.value;
            } catch (error) {
                console.error('Error updating brand color:', error);
                displayError('Failed to update brand color');
            }
        });
    });

    // Initialize hero text color pickers (Subpage specific)
    const heroColorInputs = [
        'hero_heading_color', 
        'hero_subheading_color',
        'banner_2_heading_color',
        'banner_2_subheading_color',
        'banner_3_heading_color',
        'banner_3_subheading_color'
    ];
    
    heroColorInputs.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('input', async function() {
                try {
                    await smartUpdate(context, {
                        fieldType: 'color',
                        fieldName: id,
                        value: this.value,
                        previousValue: this.defaultValue,
                        page_type: context.pageSelector.value,
                        isGlobal: false,  // Hero colors are subpage-specific
                        return_preview: true
                    });
                    // Update the defaultValue for future changes
                    this.defaultValue = this.value;
                } catch (error) {
                    console.error(`Error updating ${id}:`, error);
                    displayError(`Failed to update ${id.replace(/_/g, ' ')}`);
                }
            });
        } else {
            console.warn(`Failed to find element: ${id}`);
        }
    });
}