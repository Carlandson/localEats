import { getCookie } from './cookies.js';
import { displayError } from './errors.js';
import { reinitializeSlider } from '../components/heroComponents.js';

export async function updatePreview(pageType, context) {
    console.log('updatePreview called with:', { pageType, context });

    if (!pageType || !context?.business_subdirectory) {
        console.error('Missing required parameters:', { pageType, context });
        throw new Error('Missing required parameters for preview update');
    }

    try {
        const url = `/${context.business_subdirectory}/preview-page/${pageType}/`;
        console.log('Fetching preview from:', url);

        const response = await fetch(url, {
            headers: {
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Accept': 'text/html'
            },
            credentials: 'same-origin'
        });
        
        if (!response.ok) {
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Server error: ${response.status}`);
            } else {
                const errorText = await response.text();
                throw new Error(`Server error: ${response.status}`);
            }
        }

        const html = await response.text();
        const previewContainer = document.getElementById('page-content-preview');
        if (!previewContainer) {
            throw new Error('Preview container not found in DOM');
        }


        
        // Update the preview content
        previewContainer.innerHTML = html;
        
        const sliderContainer = previewContainer.querySelector('.slider-container');
        if (sliderContainer) {
            console.log('Banner slider detected, initializing...');
            reinitializeSlider();
        }
        return true;

    } catch (error) {
        console.error('Preview update error:', {
            message: error.message,
            url: `/${context.business_subdirectory}/preview-page/${pageType}/`,
            context: context,
            pageType: pageType
        });
        displayError(`Preview update failed: ${error.message}`);
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