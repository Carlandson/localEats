import { updateGlobalComponent } from '../components/globalComponents.js';
import { displayError } from '../utils/errors.js';
import { updatePreview } from '../utils/previewUpdates.js';

function getLayoutElements() {
    const navInputs = document.querySelectorAll('input[name="nav_style"]');
    const footerInputs = document.querySelectorAll('input[name="footer_style"]');
    
    console.log('Found nav inputs:', navInputs.length);
    console.log('Nav inputs:', Array.from(navInputs).map(input => input.value));
    console.log('Found footer inputs:', footerInputs.length);
    
    return {
        navStyleInputs: navInputs,
        footerStyleInputs: footerInputs
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
                await updatePreview(context.pageSelector.value);
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
                await updatePreview(context.pageSelector.value);
            } catch (error) {
                console.error('Error updating footer style:', error);
                displayError('Failed to update footer style');
            }
        });
    });

    // Return true if initialization was successful
    return true;
}