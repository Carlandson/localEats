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

export function initializeAddPageDropdown(context) {
    const addPageDropdown = document.getElementById('available-pages');
    const pageSelector = document.getElementById('page-selector');
    
    if (addPageDropdown) {
        addPageDropdown.addEventListener('change', async function() {
            const selectedPageType = this.value;
            console.log('Selected page type:', selectedPageType);
            if (!selectedPageType) return;

            try {
                // Use smartUpdate to create the new page
                const response = await smartUpdate(context, {
                    fieldType: 'new_page',
                    page_type: selectedPageType,
                    return_preview: true
                });

                if (response.success) {
                    // Reset the add page dropdown
                    this.value = '';
                    
                    // Update the page selector and load the new page directly
                    if (pageSelector) {
                        pageSelector.value = selectedPageType;
                        // Load the page data directly instead of triggering change event
                        await loadPageData(selectedPageType, context);
                    }
                } else {
                    console.error('Failed to create page:', response.error);
                }
            } catch (error) {
                console.error('Error creating new page:', error);
                // Reset the dropdown on error
                this.value = '';
            }
        });
    }
}