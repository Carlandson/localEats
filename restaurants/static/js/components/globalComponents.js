import { getCookie } from '../utils/cookies.js';
import { displayError } from '../utils/errors.js';
import { updatePreview } from '../utils/previewUpdates.js';
import { handleBannerSliderVisibility } from './heroComponents.js';

export async function updateGlobalComponent(component, style, context) {
    const { business_subdirectory, pageSelector } = context;
    
    try {
        console.log('updateGlobalComponent called with:', {
            component,
            style,
            business_subdirectory,
            pageType: pageSelector.value
        });

        // Handle banner slider visibility if this is a hero layout update
        if (component === 'hero_layout') {
            console.log('Updating banner slider visibility:', style);
            handleBannerSliderVisibility(style);
        }

        const requestBody = {
            component: component,
            style: style
        };
        
        // Add page type to URL as query parameter
        const url = `/${business_subdirectory}/update-global-component/?page_type=${pageSelector.value}`;
        console.log('Sending request to:', url);
        console.log('With body:', requestBody);

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify(requestBody)
        });

        console.log('Response status:', response.status);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to update component');
        }
        
        const data = await response.json();
        console.log('Update response:', data);
        
        if (data.success) {
            // Update preview after successful component change
            await updatePreview(pageSelector.value, context, false);
            return true;
        } else {
            throw new Error(data.error || 'Update failed');
        }
    } catch (error) {
        console.error('Error in updateGlobalComponent:', error);
        displayError('Failed to update component: ' + error.message);
        throw error;
    }
}

export async function togglePagePublish(isPublished, context) {
    const { business_subdirectory, pageSelector } = context;
    
    try {
        console.log('togglePagePublish called with:', {
            isPublished,
            business_subdirectory,
            pageType: pageSelector.value
        });

        const response = await fetch(`/${business_subdirectory}/toggle-publish/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                page_type: pageSelector.value,
                is_published: isPublished
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to update publish status');
        }

        const data = await response.json();
        console.log('Publish toggle response:', data);

        if (data.success) {
            // Update the status text and any UI elements
            const publishStatus = document.getElementById('publish-status');
            if (publishStatus) {
                publishStatus.textContent = isPublished ? 'Published' : 'Draft';
                publishStatus.classList.add('text-blue-600');
                setTimeout(() => {
                    publishStatus.classList.remove('text-blue-600');
                }, 1000);
            }
            return true;
        } else {
            throw new Error(data.error || 'Update failed');
        }
    } catch (error) {
        console.error('Error in togglePagePublish:', error);
        displayError('Failed to update publish status: ' + error.message);
        throw error;
    }
}