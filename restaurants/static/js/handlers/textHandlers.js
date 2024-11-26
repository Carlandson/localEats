import { debounce } from '../utils/debounce.js';
import { displayError } from '../utils/errors.js';
import { getCookie } from '../utils/cookies.js';
import { updatePreview } from '../utils/previewUpdates.js';

export function getTextElements() {
    return {
        headingInput: document.getElementById('hero-heading'),
        subheadingInput: document.getElementById('hero-subheading'),
        showHeadingCheckbox: document.getElementById('show-hero-heading'),
        showSubheadingCheckbox: document.getElementById('show-hero-subheading'),
        bannerTwoHeadingInput: document.getElementById('banner-2-heading'),
        bannerOneSubheadingInput: document.getElementById('banner-2-subheading'),
        showBannerOneCheckbox: document.getElementById('show-banner-2'),
        bannerThreeHeadingInput: document.getElementById('banner-3-heading'),
        bannerThreeSubheadingInput: document.getElementById('banner-3-subheading'),
        showBannerThreeCheckbox: document.getElementById('show-banner-3')
    };
}

export function initializeTextInputs(context) {
    const elements = getTextElements();
    
    // Initialize heading checkbox
    if (elements.showHeadingCheckbox) {
        elements.showHeadingCheckbox.checked = elements.showHeadingCheckbox.dataset.initialState === 'true';
        
        elements.showHeadingCheckbox.addEventListener('change', async function() {
            if (elements.headingInput) {
                elements.headingInput.disabled = !this.checked;
            }
            await updateHeroText('show-hero-heading', this.checked, context);
            
            if (this.checked && elements.headingInput && elements.headingInput.value) {
                await updateHeroText('hero-heading', elements.headingInput.value, context);
            }
        });
    }

    // Initialize subheading checkbox
    if (elements.showSubheadingCheckbox) {
        elements.showSubheadingCheckbox.checked = elements.showSubheadingCheckbox.dataset.initialState === 'true';
        
        elements.showSubheadingCheckbox.addEventListener('change', async function() {
            if (elements.subheadingInput) {
                elements.subheadingInput.disabled = !this.checked;
            }
            await updateHeroText('show-hero-subheading', this.checked, context);
            
            if (this.checked && elements.subheadingInput && elements.subheadingInput.value) {
                await updateHeroText('hero-subheading', elements.subheadingInput.value, context);
            }
        });
    }

    // Initialize text inputs with debounce
    [elements.headingInput, elements.subheadingInput].forEach(input => {
        if (input) {
            input.addEventListener('input', debounce(async function() {
                await updateHeroText(this.id, this.value, context);
            }, 500));
        }
    });
}

export async function updateHeroText(field, value, context) {
    console.log(`Attempting to update ${field} to:`, value);
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