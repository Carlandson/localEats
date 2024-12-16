import { displayError } from '../utils/errors.js';
import { smartUpdate } from '../utils/previewUpdates.js';

export function initializeHeroSizeHandler(context) {
    const heroSizeSelect = document.querySelector('select[name="hero_size"]');
    
    if (heroSizeSelect) {
        heroSizeSelect.addEventListener('change', async function() {
            try {
                console.log('Hero size changed to:', this.value);
                const previousValue = this.defaultValue;
                
                await smartUpdate(context, {
                    fieldType: 'size',
                    fieldName: 'hero_size',
                    value: this.value,
                    previousValue: previousValue,
                    page_type: context.pageSelector.value,
                    isGlobal: false  // Since hero size is a global setting
                });

                // Update the default value after successful update
                this.defaultValue = this.value;
                
            } catch (error) {
                console.error('Error updating hero size:', error);
                displayError('Failed to update hero size');
                // Revert to previous value on error
                this.value = this.defaultValue;
            }
        });
    }
}