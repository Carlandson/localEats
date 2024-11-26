import { getCookie } from './cookies.js';
import { displayError } from './errors.js';

export async function updatePreview(pageType, context) {
    try {
        const response = await fetch(`/${context.business_subdirectory}/preview/${pageType}/`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (!response.ok) {
            throw new Error('Failed to update preview');
        }

        const data = await response.json();
        if (data.success) {
            // Update the preview iframe if it exists
            const previewFrame = document.getElementById('preview-frame');
            if (previewFrame) {
                previewFrame.contentWindow.location.reload();
            }
        } else {
            throw new Error(data.error || 'Preview update failed');
        }
    } catch (error) {
        console.error('Error updating preview:', error);
        displayError('Failed to update preview');
        throw error;
    }
}

// Optional: Add function for specific component updates
export async function updateComponentPreview(component, value, context) {
    try {
        const response = await fetch(`/${context.business_subdirectory}/preview-component/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                component,
                value,
                page_type: context.pageSelector.value
            })
        });

        if (!response.ok) {
            throw new Error('Failed to update component preview');
        }

        const data = await response.json();
        if (!data.success) {
            throw new Error(data.error || 'Component preview update failed');
        }
    } catch (error) {
        console.error('Error updating component preview:', error);
        displayError('Failed to update component preview');
        throw error;
    }
}