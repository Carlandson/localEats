import { getCookie } from './cookies.js';
import { displayError } from './errors.js';
import { reinitializeSlider, handleBannerSliderVisibility } from '../components/heroComponents.js';

export async function updatePreview(pageType, context, isInitialLoad = false) {
    if (!pageType || !context?.business_subdirectory) {
        console.error('Missing required parameters:', { pageType, context });
        throw new Error('Missing required parameters for preview update');
    }

    try {
        const url = `/${context.business_subdirectory}/preview-page/${pageType}/`;

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
        if (sliderContainer && !isInitialLoad) {
            handleBannerSliderVisibility('banner-slider');
        }
        else {
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

        // Find all elements that might contain this component's content
        const componentElements = document.querySelectorAll(`[data-component="${component}"]`);
        componentElements.forEach(element => {
            // Preserve the element's attributes and only update its text content
            if (data.text) {
                // Keep the element's HTML structure but update text
                const currentHTML = element.innerHTML;
                const wrapper = document.createElement('div');
                wrapper.innerHTML = currentHTML;
                
                // Find the text node and update it
                const textNodes = Array.from(wrapper.childNodes).filter(node => 
                    node.nodeType === Node.TEXT_NODE
                );
                if (textNodes.length > 0) {
                    textNodes[0].textContent = data.text;
                } else {
                    // If no text node exists, create one
                    element.textContent = data.text;
                }
            } else if (value) {
                element.textContent = value;
            }
        });

    } catch (error) {
        console.error('Error updating component preview:', error);
        displayError('Failed to update component preview');
        throw error;
    }
}