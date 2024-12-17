import { displayError } from '../utils/errors.js';
import { smartUpdate } from '../utils/previewUpdates.js';

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
            
            try {
                const currentPage = context.pageSelector.value;
                console.log('Updating heading visibility for page:', currentPage);
                
                await smartUpdate(context, {
                    fieldType: 'toggle',
                    fieldName: showHeadingId,
                    value: this.checked,
                    previousValue: !this.checked,
                    page_type: currentPage,  // Use current page from selector
                    isGlobal: false,
                    return_preview: true
                });
            } catch (error) {
                console.error('Error updating heading visibility:', error);
                displayError('Failed to update heading visibility');
                // Revert the checkbox state on error
                this.checked = !this.checked;
            }
        });
    }

    if (showSubheading) {
        showSubheading.checked = showSubheading.dataset.initialState === 'true';
        
        showSubheading.addEventListener('change', async function() {
            if (subheadingInput) {  // Fixed: was using headingInput
                subheadingInput.disabled = !this.checked;
            }
            
            try {
                const currentPage = context.pageSelector.value;
                console.log('Updating subheading visibility for page:', currentPage);
                
                await smartUpdate(context, {
                    fieldType: 'toggle',
                    fieldName: showSubheadingId,
                    value: this.checked,
                    previousValue: !this.checked,
                    page_type: currentPage,  // Use current page from selector
                    isGlobal: false,
                    return_preview: true
                });
            } catch (error) {
                console.error('Error updating subheading visibility:', error);
                displayError('Failed to update subheading visibility');
                // Revert the checkbox state on error
                this.checked = !this.checked;
            }
        });
    }

    // Initialize text inputs
    [headingInput, subheadingInput].forEach(input => {
        if (input) {
            let lastValue = input.value;  // Store initial value
            
            input.addEventListener('input', async function() {
                try {
                    const currentPage = context.pageSelector.value;
                    console.log(`Updating ${this.id} for page:`, currentPage);
                    
                    await smartUpdate(context, {
                        fieldType: 'text',
                        fieldName: this.id,
                        value: this.value,
                        previousValue: lastValue,
                        page_type: currentPage,  // Use current page from selector
                        isGlobal: false,
                        return_preview: true
                    });
                    
                    // Update lastValue after successful update
                    lastValue = this.value;
                    
                } catch (error) {
                    console.error('Error updating text:', error);
                    displayError('Failed to update text');
                    // Revert to last known good value on error
                    this.value = lastValue;
                }
            });
        }
    });
}

export function initializeTextInputs(context) {
    initializeBannerText('hero', context);
    initializeBannerText('banner_2', context);
    initializeBannerText('banner_3', context);
}

// export async function updateHeroText(field, value, context) {
//     console.log(`Attempting to update ${field} to:`, value);
//     console.log('Full payload:', {
//         field: field,
//         value: value,
//         page_type: context.pageSelector.value
//     });
//     try {
//         const response = await fetch(`/${context.business_subdirectory}/update-hero/`, {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//                 'X-CSRFToken': getCookie('csrftoken'),
//             },
//             body: JSON.stringify({
//                 field: field,
//                 value: value,
//                 page_type: context.pageSelector.value
//             })
//         });

//         if (!response.ok) {
//             const errorData = await response.json();
//             console.error('Update failed:', errorData);
//             throw new Error(errorData.error || 'Failed to update text');
//         }

//         const data = await response.json();
//         console.log('Update response:', data);
//         if (data.success) {
//             console.log('Updating component preview');
//             await updatePreview(context.pageSelector.value, context, false);
//             // await updateComponentPreview(field, value, context, false);
//         } else {
//             throw new Error(data.error || 'Update failed');
//         }
//     } catch (error) {
//         console.error('Error:', error);
//         displayError('Failed to update text: ' + error.message);
//     }
// }