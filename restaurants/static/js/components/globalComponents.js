import { getCookie } from '../utils/cookies.js';
import { displayError } from '../utils/errors.js';
import { smartUpdate } from '../utils/previewUpdates.js';
import { handleBannerSliderVisibility } from './heroComponents.js';

export async function updateGlobalComponent(component, style, context) {
    try {
        console.log('updateGlobalComponent called with:', {
            component,
            style,
            business_subdirectory: context.business_subdirectory,
            pageType: context.pageSelector.value
        });

        // Handle banner slider visibility if this is a hero layout update
        if (component === 'hero_layout') {
            console.log('Updating banner slider visibility:', style);
            handleBannerSliderVisibility(style);
        }

        // Map component names to field names if needed
        const fieldNameMap = {
            'navigation': 'navigation_style',
            'footer_style': 'footer_style',
            'hero_layout': 'hero_layout',
            'hero_size': 'hero_size'
        };

        const fieldName = fieldNameMap[component] || component;

        // Get the current value before updating
        let previousValue;
        const radioInput = document.querySelector(`input[name="${component}"]:checked`);
        const selectInput = document.querySelector(`select[name="${component}"]`);
        
        if (radioInput) {
            previousValue = radioInput.value;
        } else if (selectInput) {
            previousValue = selectInput.value;
        }

        console.log('Previous value:', previousValue); // Debug log

        const response = await smartUpdate(context, {
            fieldType: 'layout',
            fieldName: fieldName,
            value: style,
            previousValue: previousValue,
            page_type: context.pageSelector.value,
            isGlobal: true,
            return_preview: true
        });

        // Update the input value after successful update
        if (radioInput) {
            radioInput.value = style;
        } else if (selectInput) {
            selectInput.value = style;
        }

        return response;

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

        // Use smartUpdate for publish status
        await smartUpdate(context, {
            fieldType: 'toggle',
            fieldName: 'is_published',
            value: isPublished,
            previousValue: !isPublished,
            page_type: pageSelector.value,
            return_preview: true
        });

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

    } catch (error) {
        console.error('Error in togglePagePublish:', error);
        displayError('Failed to update publish status: ' + error.message);
        throw error;
    }
}