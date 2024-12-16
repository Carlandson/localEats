import { smartUpdate } from '../utils/previewUpdates.js';
import { displayError } from '../utils/errors.js';

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
            const previousValue = !this.checked;
            await smartUpdate(context, {
                fieldType: 'toggle',
                fieldName: 'is_published',
                value: this.checked,
                previousValue: previousValue,
                page_type: context.pageSelector.value,
                return_preview: true,
                isGlobal: false
            });

            // Update status text after successful update
            if (publishStatus) {
                publishStatus.textContent = this.checked ? 'Published' : 'Draft';
            }
        } catch (error) {
            console.error('Error updating publish state:', error);
            // Revert on error (handled by smartUpdate)
            if (publishStatus) {
                publishStatus.textContent = !this.checked ? 'Published' : 'Draft';
            }
            displayError('Failed to update publish state');
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