import { debounce } from '../utils/debounce.js';
import { displayError } from '../utils/errors.js';
import { getCookie } from '../utils/cookies.js';
import { updatePreview } from '../utils/previewUpdates.js';

function initializeBannerText(prefix, context) {
    const showHeadingId = `show_${prefix}_heading`;
    const showSubheadingId = `show_${prefix}_subheading`;
    const headingId = `${prefix}_heading`;
    const subheadingId = `${prefix}_subheading`;

    // Get elements
    const showHeading = document.getElementById(showHeadingId);
    const showSubheading = document.getElementById(showSubheadingId);
    const headingInput = document.getElementById(headingId);
    const subheadingInput = document.getElementById(subheadingId);

    // Initialize heading checkbox
    if (showHeading) {
        showHeading.checked = showHeading.dataset.initialState === 'true';
        
        showHeading.addEventListener('change', async function() {
            if (headingInput) {
                headingInput.disabled = !this.checked;
            }
            await updateHeroText(showHeadingId, this.checked, context);
            
            if (this.checked && headingInput && headingInput.value) {
                await updateHeroText(headingId, headingInput.value, context);
            }
        });
    }

    // Initialize subheading checkbox
    if (showSubheading) {
        showSubheading.checked = showSubheading.dataset.initialState === 'true';
        
        showSubheading.addEventListener('change', async function() {
            if (subheadingInput) {
                subheadingInput.disabled = !this.checked;
            }
            await updateHeroText(showSubheadingId, this.checked, context);
            
            if (this.checked && subheadingInput && subheadingInput.value) {
                await updateHeroText(subheadingId, subheadingInput.value, context);
            }
        });
    }

    // Initialize text inputs with debounce
    [headingInput, subheadingInput].forEach(input => {
        if (input) {
            input.addEventListener('input', debounce(async function() {
                await updateHeroText(this.id, this.value, context);
            }, 500));
        }
    });
}

export function initializeTextInputs(context) {
    // Initialize all banners
    initializeBannerText('hero', context);
    initializeBannerText('hero_banner_2', context);
    initializeBannerText('hero_banner_3', context);
}

export async function updateHeroText(field, value, context) {
    console.log(`Attempting to update ${field} to:`, value);
    console.log('Full payload:', {
        field: field,
        value: value,
        page_type: context.pageSelector.value
    });
    try {
        const response = await fetch(`/${context.business_subdirectory}/update-hero/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                field: field,
                value: value,
                page_type: context.pageSelector.value
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('Update failed:', errorData);
            throw new Error(errorData.error || 'Failed to update text');
        }

        const data = await response.json();
        console.log('Update response:', data);
        if (data.success) {
            await updatePreview(context.pageSelector.value, context);
        } else {
            throw new Error(data.error || 'Update failed');
        }
    } catch (error) {
        console.error('Error:', error);
        displayError('Failed to update text: ' + error.message);
    }
}