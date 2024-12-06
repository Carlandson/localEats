import { getCookie } from './cookies.js';
import { displayError } from './errors.js';

export async function updateHeroText(field, value, context) {
    try {
        const response = await fetch(`/${context.business_subdirectory}/update-hero/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                field,
                value,
                page_type: context.pageSelector.value
            })
        });

        if (!response.ok) {
            throw new Error('Failed to update hero text');
        }

        const data = await response.json();
        if (data.success) {
            await updatePreview(context.pageSelector.value, context, false);
        } else {
            throw new Error(data.error || 'Update failed');
        }
    } catch (error) {
        console.error('Error updating hero text:', error);
        displayError('Failed to update hero text');
        throw error;
    }
}