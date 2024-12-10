import { updateGlobalComponent } from '../components/globalComponents.js';

export function initializePublishToggle(context) {
    const publishToggle = document.getElementById('publish-toggle');
    const publishStatus = document.getElementById('publish-status');
    
    if (!publishToggle) {
        console.warn('Publish toggle element not found');
        return;
    }

    // Remove existing listeners
    const newToggle = publishToggle.cloneNode(true);
    publishToggle.parentNode.replaceChild(newToggle, publishToggle);

    newToggle.addEventListener('change', async function() {
        try {
            // Get current page type from the selector
            const currentPage = context.pageSelector.value;
            const updatedContext = {
                ...context,
                pageType: currentPage  // Add current page type to context
            };

            const success = await updateGlobalComponent('is_published', this.checked, updatedContext);
            if (success) {
                if (publishStatus) {
                    publishStatus.textContent = this.checked ? 'Published' : 'Draft';
                }
            } else {
                // Revert on failure
                this.checked = !this.checked;
                if (publishStatus) {
                    publishStatus.textContent = this.checked ? 'Published' : 'Draft';
                }
            }
        } catch (error) {
            console.error('Error updating publish state:', error);
            // Revert on error
            this.checked = !this.checked;
            if (publishStatus) {
                publishStatus.textContent = this.checked ? 'Published' : 'Draft';
            }
        }
    });
}

export function updatePublishState(isPublished) {
    const publishToggle = document.getElementById('publish-toggle');
    const publishStatus = document.getElementById('publish-status');
    
    if (publishToggle) {
        publishToggle.checked = isPublished;
    }
    
    if (publishStatus) {
        publishStatus.textContent = isPublished ? 'Published' : 'Draft';
    }
}