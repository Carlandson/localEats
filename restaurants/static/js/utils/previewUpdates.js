import { getCookie } from './cookies.js';
import { displayError } from './errors.js';
import { reinitializeSlider, handleBannerSliderVisibility } from '../components/heroComponents.js';
import { PreviewCache } from './cache.js';
import { debounce } from './debounce.js';

const previewCache = new PreviewCache();

const UPDATE_STRATEGIES = {
    IMMEDIATE: 'immediate',   // For critical updates
    DEBOUNCED: 'debounced',  // For text input
    OPTIMISTIC: 'optimistic', // For simple UI changes
    COMBINED: 'combined'      // For complex updates
};

async function handleImageUpdate(context, data) {
    console.log('handleImageUpdate called with:', data);
    
    if (data.isImageRemoval) {
        console.log('Handling image removal');
        return await fetch(`/${context.business_subdirectory}/remove-hero-image/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                page_type: data.page_type,
                banner_type: data.fieldName,
                return_preview: true
            })
        });
    } else {
        console.log('Handling image upload');
        const formData = new FormData();
        formData.append('image', data.value);
        formData.append('page_type', data.page_type);
        formData.append('banner_type', data.fieldName);
        formData.append('return_preview', 'true');

        const response = await fetch(`/${context.business_subdirectory}/upload-hero-image/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: formData
        });

        const responseData = await response.json();
        console.log('Upload response:', responseData);

        // Store the image URL in context for the placeholder update
        if (responseData.success && responseData.image_url) {
            context.lastUploadedImageUrl = responseData.image_url;
        }

        // Create a new Response with the same data to maintain compatibility
        return new Response(JSON.stringify(responseData), {
            status: response.status,
            headers: { 'Content-Type': 'application/json' }
        });
    }
}
// Determine which strategy to use based on field type
function getUpdateStrategy(fieldType) {
    switch (fieldType) {
        case 'text':
        case 'input':
        case 'color':
            return UPDATE_STRATEGIES.DEBOUNCED;
        case 'toggle':
        case 'alignment':
        case 'font':
        case 'size':
        case 'button':
            return UPDATE_STRATEGIES.OPTIMISTIC;
        case 'layout':
        case 'image':
            return UPDATE_STRATEGIES.COMBINED;
        case 'preview':
        case 'load_page':
        case 'initialize':
            return UPDATE_STRATEGIES.IMMEDIATE;
        default:
            return UPDATE_STRATEGIES.IMMEDIATE;
    }
}

export async function smartUpdate(context, data) {
    const strategy = getUpdateStrategy(data.fieldType);
    
    switch (strategy) {
        case UPDATE_STRATEGIES.DEBOUNCED:
            return debouncedUpdate(context, data);
        case UPDATE_STRATEGIES.OPTIMISTIC:
            return optimisticUpdate(context, data);
        case UPDATE_STRATEGIES.COMBINED:
            return combinedUpdate(context, data);
        default:
            return immediateUpdate(context, data);
    }
}

const debouncedUpdate = debounce(async (context, data) => {
    try {
        await combinedUpdate(context, data);
    } catch (error) {
        console.error('Debounced update failed:', error);
        displayError('Failed to update content');
    }
}, 500);

async function optimisticUpdate(context, data) {
    console.log('Attempting optimistic update with data:', data);
    // Update UI immediately
    updateLocalUI(data);
    console.log('Local UI updated');
    
    try {
        // Send update to server in background
        const response = await fetch(`/api/${context.business_subdirectory}/layout/update/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                ...data,
                return_preview: true  // Request preview HTML
            })
        });

        if (!response.ok) {
            throw new Error('Server update failed');
        }

        // Process the response and update preview
        const responseData = await response.json();
        if (responseData.preview_html) {
            const previewContainer = document.getElementById('page-content-preview');
            if (previewContainer) {
                previewContainer.innerHTML = responseData.preview_html;
                reinitializeSlider();
            }
        }

        return responseData;

    } catch (error) {
        // Revert UI on error
        revertLocalUI(data);
        throw error;
    }
}

// Combined updates (single request for data + preview)
async function combinedUpdate(context, data) {
    try {
        let response;
        if (data.fieldType === 'image') {
            console.log('handleimageupdate')
            response = await handleImageUpdate(context, data);
        } else {
            console.log('Sending combined update request:', data); // Debug log
            response = await fetch(`/api/${context.business_subdirectory}/layout/update/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    ...data,
                    return_preview: true
                })
            });
        }

        if (!response.ok) {
            throw new Error('Server update failed');
        }

        // Handle preview update
        const responseData = await response.json();
        console.log('Combined update response:', responseData); // Debug log
        
        if (responseData.preview_html) {
            const previewContainer = document.getElementById('page-content-preview');
            console.log('Preview container found:', !!previewContainer); // Debug log
            if (previewContainer) {
                previewContainer.innerHTML = responseData.preview_html;
                console.log('Preview container updated');
                reinitializeSlider();
            }
        } else {
            console.log('No preview HTML in response'); // Debug log
        }

        return responseData;
    } catch (error) {
        console.error('Combined update failed:', error);
        throw error;
    }
}

async function immediateUpdate(context, data) {
    try {
        console.log('Performing immediate update with:', data);
        
        // Special handling for initialization and page loading
        if (data.fieldType === 'initialize' || data.fieldType === 'load_page') {
            const response = await fetch(`/${context.business_subdirectory}/get-page-data/${data.page_type}/`);
            
            if (!response.ok) {
                throw new Error('Failed to load page data');
            }

            const responseData = await response.json();
            
            // If we need preview HTML, fetch it separately
            if (data.return_preview) {
                const previewResponse = await fetch(`/${context.business_subdirectory}/preview-page/${data.page_type}/`, {
                    headers: {
                        'Cache-Control': 'no-cache',
                        'Pragma': 'no-cache',
                        'Accept': 'text/html'
                    }
                });

                if (previewResponse.ok) {
                    responseData.preview_html = await previewResponse.text();
                }
            }

            return responseData;
        }
        
        // Regular immediate updates
        const response = await fetch(`/api/${context.business_subdirectory}/layout/update/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                ...data,
                return_preview: true
            })
        });

        if (!response.ok) {
            throw new Error('Server update failed');
        }

        const responseData = await response.json();
        
        // Update preview if available
        if (responseData.preview_html) {
            const previewContainer = document.getElementById('page-content-preview');
            if (previewContainer) {
                previewContainer.innerHTML = responseData.preview_html;
                reinitializeSlider();
            }
        }

        return responseData;
    } catch (error) {
        console.error('Immediate update failed:', error);
        displayError('Failed to update content');
        throw error;
    }
}

// Helper functions for optimistic updates
function updateLocalUI(data) {
    console.log('Updating local UI with:', data);
    
    switch (data.fieldType) {
        case 'text':
            const textElement = document.getElementById(data.fieldName);
            if (textElement) textElement.value = data.value;
            break;

        case 'color':
            const colorElement = document.getElementById(data.fieldName);
            if (colorElement) {
                colorElement.value = data.value;
                // Update any preview elements that use this color
                const previewElements = document.querySelectorAll(`[data-preview-color="${data.fieldName}"]`);
                previewElements.forEach(element => {
                    if (element.tagName.toLowerCase() === 'input') {
                        element.value = data.value;
                    } else {
                        element.style.color = data.value;
                    }
                });
            }
            break;

        case 'font':
            const fontElement = document.getElementById(data.fieldName);
            if (fontElement) {
                fontElement.value = data.value;
                // Update any preview elements that use this font
                const fontPreviewElements = document.querySelectorAll(`[data-preview-font="${data.fieldName}"]`);
                fontPreviewElements.forEach(element => {
                    element.style.fontFamily = data.value;
                });
            }
            break;

        case 'size':
            const sizeElement = document.getElementById(data.fieldName);
            if (sizeElement) {
                sizeElement.value = data.value;
                // Update any preview elements that use this size
                const sizePreviewElements = document.querySelectorAll(`[data-preview-size="${data.fieldName}"]`);
                sizePreviewElements.forEach(element => {
                    element.style.fontSize = data.value;
                });
            }
            break;

        case 'toggle':
            const toggleElement = document.getElementById(data.fieldName);
            if (toggleElement) toggleElement.checked = data.value;
            break;

        case 'alignment':
            const alignmentRadio = document.querySelector(`input[name="${data.fieldName}"][value="${data.value}"]`);
            if (alignmentRadio) alignmentRadio.checked = true;
            break;

        case 'button':
            const buttonElement = document.getElementById(data.fieldName);
            if (buttonElement) {
                if (data.fieldName.includes('color')) {
                    buttonElement.value = data.value;
                    // Update button preview styles
                    const buttonPreview = document.querySelector(`[data-preview-button="${data.fieldName}"]`);
                    if (buttonPreview) {
                        if (data.fieldName.includes('bg')) {
                            buttonPreview.style.backgroundColor = data.value;
                        } else if (data.fieldName.includes('text')) {
                            buttonPreview.style.color = data.value;
                        } else if (data.fieldName.includes('border')) {
                            buttonPreview.style.borderColor = data.value;
                        }
                    }
                } else {
                    buttonElement.value = data.value;
                }
            }
            break;
    }
}


function revertLocalUI(data) {
    console.log('Reverting local UI with:', data);
    
    switch (data.fieldType) {
        case 'text':
        case 'color':
        case 'font':
        case 'size':
            const element = document.getElementById(data.fieldName);
            if (element) element.value = data.previousValue;
            break;

        case 'toggle':
            const toggleElement = document.getElementById(data.fieldName);
            if (toggleElement) toggleElement.checked = data.previousValue;
            break;

        case 'alignment':
            const alignmentRadio = document.querySelector(`input[name="${data.fieldName}"][value="${data.previousValue}"]`);
            if (alignmentRadio) alignmentRadio.checked = true;
            break;

        case 'button':
            const buttonElement = document.getElementById(data.fieldName);
            if (buttonElement) buttonElement.value = data.previousValue;
            break;
    }

    // Revert any preview elements
    const previewElements = document.querySelectorAll(`[data-preview-${data.fieldType}="${data.fieldName}"]`);
    previewElements.forEach(element => {
        switch (data.fieldType) {
            case 'color':
                element.style.color = data.previousValue;
                break;
            case 'font':
                element.style.fontFamily = data.previousValue;
                break;
            case 'size':
                element.style.fontSize = data.previousValue;
                break;
            case 'button':
                if (data.fieldName.includes('bg')) {
                    element.style.backgroundColor = data.previousValue;
                } else if (data.fieldName.includes('text')) {
                    element.style.color = data.previousValue;
                } else if (data.fieldName.includes('border')) {
                    element.style.borderColor = data.previousValue;
                }
                break;
        }
    });
}


// old updatePreview function
export async function updatePreview(pageType, context, isInitialLoad = false) {
    if (!pageType || !context?.business_subdirectory) {
        console.error('Missing required parameters:', { pageType, context });
        throw new Error('Missing required parameters for preview update');
    }

    try {
        // If it's the initial load and we have initialHtml in the context, use that
        if (isInitialLoad && context.initialHtml) {
            const previewContainer = document.getElementById('page-content-preview');
            if (!previewContainer) {
                throw new Error('Preview container not found in DOM');
            }
            
            previewContainer.innerHTML = context.initialHtml;
            reinitializeSlider();
            return true;
        }

        // Use smartUpdate to get the preview HTML
        const response = await smartUpdate(context, {
            fieldType: 'preview',
            page_type: pageType,
            return_preview: true
        });

        const previewContainer = document.getElementById('page-content-preview');
        if (!previewContainer) {
            throw new Error('Preview container not found in DOM');
        }

        // Update the preview content
        if (response.preview_html) {
            previewContainer.innerHTML = response.preview_html;
            
            const sliderContainer = previewContainer.querySelector('.slider-container');
            if (sliderContainer && !isInitialLoad) {
                handleBannerSliderVisibility('banner-slider');
            } else {
                reinitializeSlider();
            }
        }

        return true;

    } catch (error) {
        console.error('Preview update error:', {
            message: error.message,
            context: context,
            pageType: pageType
        });
        displayError(`Preview update failed: ${error.message}`);
        throw error;
    }
}


// Optional: Add function for specific component updates
// export async function updateComponentPreview(component, value, context) {
//     try {
//         const response = await fetch(`/${context.business_subdirectory}/preview-component/`, {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//                 'X-CSRFToken': getCookie('csrftoken'),
//             },
//             body: JSON.stringify({
//                 component,
//                 value,
//                 page_type: context.pageSelector.value
//             })
//         });

//         if (!response.ok) {
//             throw new Error('Failed to update component preview');
//         }

//         const data = await response.json();
//         if (!data.success) {
//             throw new Error(data.error || 'Component preview update failed');
//         }

//         // Find all elements that might contain this component's content
//         const componentElements = document.querySelectorAll(`[data-component="${component}"]`);
//         componentElements.forEach(element => {
//             // Preserve the element's attributes and only update its text content
//             if (data.text) {
//                 // Keep the element's HTML structure but update text
//                 const currentHTML = element.innerHTML;
//                 const wrapper = document.createElement('div');
//                 wrapper.innerHTML = currentHTML;
                
//                 // Find the text node and update it
//                 const textNodes = Array.from(wrapper.childNodes).filter(node => 
//                     node.nodeType === Node.TEXT_NODE
//                 );
//                 if (textNodes.length > 0) {
//                     textNodes[0].textContent = data.text;
//                 } else {
//                     // If no text node exists, create one
//                     element.textContent = data.text;
//                 }
//             } else if (value) {
//                 element.textContent = value;
//             }
//         });

//     } catch (error) {
//         console.error('Error updating component preview:', error);
//         displayError('Failed to update component preview');
//         throw error;
//     }
// }