import { updateGlobalComponent } from '../components/globalComponents.js';

export function initializePublishToggle(context) {
    const publishToggle = document.getElementById('publish-toggle');
    
    if (!publishToggle) {
        console.warn('Publish toggle element not found');
        return;
    }

    publishToggle.addEventListener('change', async function() {
        try {
            await updateGlobalComponent('is_published', this.checked, context);
        } catch (error) {
            // Revert on error
            this.checked = !this.checked;
        }
    });
}