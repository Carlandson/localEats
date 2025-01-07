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
                console.log("smartupdate", response)
                if (response.success) {
                    // Get both dropdowns
                    const addPagesDropdown = document.getElementById('available-pages');
                    const yourPagesDropdown = document.getElementById('page-selector');
                    
                    // Remove the selected option from available pages
                    const selectedOption = addPagesDropdown.querySelector(`option[value="${selectedPageType}"]`);
                    if (selectedOption) {
                        selectedOption.remove();
                    }
                    
                    // Add the new page to your pages dropdown
                    const newOption = document.createElement('option');
                    newOption.value = selectedPageType;
                    newOption.className = 'px-2';
                    newOption.textContent = `${selectedPageType.charAt(0).toUpperCase() + selectedPageType.slice(1)} Page`;
                    yourPagesDropdown.appendChild(newOption);
                    yourPagesDropdown.value = selectedPageType;
                    // Reset the add page dropdown
                    addPagesDropdown.value = '';
                    showToast(`${selectedPageType.charAt(0).toUpperCase() + selectedPageType.slice(1)} page successfully added!`);

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

function showToast(message, duration = 3000) {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');
    toastMessage.textContent = message;
    
    // Show the toast
    toast.classList.add('toast-show');
    
    // Hide the toast after duration
    setTimeout(() => {
        toast.classList.remove('toast-show');
    }, duration);
}