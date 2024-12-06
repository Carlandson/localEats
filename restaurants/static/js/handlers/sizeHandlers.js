import { updateGlobalComponent } from '../components/globalComponents.js';
import { displayError } from '../utils/errors.js';
import { updatePreview } from '../utils/previewUpdates.js';

export function initializeHeroSizeHandler(context) {
    const heroSizeSelect = document.querySelector('select[name="hero_size"]');
    
    if (heroSizeSelect) {
        heroSizeSelect.addEventListener('change', async function() {
            try {
                console.log('Hero size changed to:', this.value);
                await updateGlobalComponent('hero_size', this.value, context);
                await updatePreview(context.pageSelector.value, context);
            } catch (error) {
                console.error('Error updating hero size:', error);
                displayError('Failed to update hero size');
            }
        });
    }
}