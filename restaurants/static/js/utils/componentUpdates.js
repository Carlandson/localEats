import { getCookie } from './cookies.js';
import { displayError } from './errors.js';
import { updatePreview } from './previewUpdates.js';

export async function updateGlobalComponent(component, value, context) {
    try {
        console.log('Updating global component', component, value, context);
        const response = await fetch(`/${context.business_subdirectory}/update-global-component/`, {
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
            throw new Error('Failed to update component');
        }

        const data = await response.json();
        if (!data.success) {
            throw new Error(data.error || 'Component update failed');
        }
        console.log('Component updated successfully', component);
        // Optionally update preview after component change
        await updatePreview(context.pageSelector.value, context, false);
    } catch (error) {
        console.error('Error updating component:', error);
        displayError(`Failed to update ${component.replace('_', ' ')}`);
        throw error;
    }
}