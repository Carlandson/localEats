import { updateGlobalComponent } from '../components/globalComponents.js';
import { displayError } from '../utils/errors.js';
import { updatePreview } from '../utils/previewUpdates.js';
import { handleBannerSliderVisibility } from '../components/heroComponents.js';
import { getCookie } from '../utils/cookies.js';

function getLayoutElements() {
    // Get all component selectors
    const navInputs = document.querySelectorAll('.component-selector[data-component="navigation"]');
    const footerInputs = document.querySelectorAll('.component-selector[data-component="footer_style"]');
    const heroLayoutInputs = document.querySelectorAll('.component-selector[data-component="hero_layout"]');
    
    console.log('Found nav inputs:', navInputs.length);
    console.log('Nav inputs:', Array.from(navInputs).map(input => input.value));
    console.log('Found footer inputs:', footerInputs.length);
    console.log('Found hero layout inputs:', heroLayoutInputs.length);
    
    return {
        navStyleInputs: navInputs,
        footerStyleInputs: footerInputs,
        heroLayoutInputs: heroLayoutInputs
    };
}

export function initializeLayoutHandlers(context) {
    console.log('Initializing layout handlers with context:', context);
    const elements = getLayoutElements();

    // Navigation Style Handlers
    elements.navStyleInputs.forEach(input => {
        console.log('Attaching nav listener to:', input.value);
        input.addEventListener('change', async function() {
            try {
                console.log('Nav style changed to:', this.value);
                await updateGlobalComponent('navigation', this.value, context);
                await updatePreview(context.pageSelector.value, context);
            } catch (error) {
                console.error('Error updating navigation style:', error);
                displayError('Failed to update navigation style');
            }
        });
    });

    // Footer Style Handlers
    elements.footerStyleInputs.forEach(input => {
        console.log('Attaching footer listener to:', input.value);
        input.addEventListener('change', async function() {
            try {
                console.log('Footer style changed to:', this.value);
                await updateGlobalComponent('footer_style', this.value, context);
                await updatePreview(context.pageSelector.value, context);
            } catch (error) {
                console.error('Error updating footer style:', error);
                displayError('Failed to update footer style');
            }
        });
    });

    // Hero Layout Style Handlers
    elements.heroLayoutInputs.forEach(input => {
        console.log('Attaching hero layout listener to:', input.value);
        input.addEventListener('change', async function() {
            try {
                console.log('Hero layout changed to:', this.value);
                
                // Update banner slider visibility first
                handleBannerSliderVisibility(this.value);

                // Send update to server
                const response = await fetch(`/${context.business_subdirectory}/update-hero/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: JSON.stringify({
                        field: 'hero_layout',
                        value: this.value,
                        page_type: context.pageSelector.value
                    })
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Failed to update hero layout');
                }

                const data = await response.json();
                if (data.success) {
                    await updatePreview(context.pageSelector.value, context);
                } else {
                    throw new Error(data.error || 'Update failed');
                }
            } catch (error) {
                console.error('Error updating hero layout style:', error);
                displayError('Failed to update hero layout style');
            }
        });
    });

    return true;
}