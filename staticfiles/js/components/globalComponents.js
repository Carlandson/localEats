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
            style: style,
            page_type: pageSelector.value
        };
        console.log('Sending request with body:', requestBody);

        const response = await fetch(`/${business_subdirectory}/update-global-component/`, {
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
            await updatePreview(pageSelector.value);
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