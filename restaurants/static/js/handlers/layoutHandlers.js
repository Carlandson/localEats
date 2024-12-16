import { displayError } from '../utils/errors.js';
import { smartUpdate } from '../utils/previewUpdates.js';
import { handleBannerSliderVisibility } from '../components/heroComponents.js';

function getLayoutElements() {
    // Get all component selectors
    const navInputs = document.querySelectorAll('.component-selector[data-component="navigation"]');
    const footerInputs = document.querySelectorAll('.component-selector[data-component="footer_style"]');
    const heroLayoutInputs = document.querySelectorAll('.component-selector[data-component="hero_layout"]'); 
    
    return {
        navStyleInputs: navInputs,
        footerStyleInputs: footerInputs,
        heroLayoutInputs: heroLayoutInputs
    };
}

export function initializeLayoutHandlers(context) {
    const elements = getLayoutElements();

    // Navigation Style Handlers
    elements.navStyleInputs.forEach(input => {
        input.addEventListener('change', async function() {
            try {
                const previousValue = this.defaultValue;
                await smartUpdate(context, {
                    fieldType: 'layout',
                    fieldName: 'navigation_style',
                    value: this.value,
                    previousValue: previousValue,
                    page_type: context.pageSelector.value,
                    isGlobal: true
                });
                this.defaultValue = this.value;
            } catch (error) {
                displayError('Failed to update navigation style');
                this.value = this.defaultValue; // Revert on error
            }
        });
    });

    // Footer Style Handlers
    elements.footerStyleInputs.forEach(input => {
        input.addEventListener('change', async function() {
            try {
                const previousValue = this.defaultValue;
                await smartUpdate(context, {
                    fieldType: 'layout',
                    fieldName: 'footer_style',
                    value: this.value,
                    previousValue: previousValue,
                    page_type: context.pageSelector.value,
                    isGlobal: true
                });
                this.defaultValue = this.value;
            } catch (error) {
                displayError('Failed to update footer style');
                this.value = this.defaultValue; // Revert on error
            }
        });
    });

    // Hero Layout Style Handlers
    elements.heroLayoutInputs.forEach(input => {
        input.addEventListener('change', async function() {
            try {
                // Update banner slider visibility first
                handleBannerSliderVisibility(this.value);

                const previousValue = this.defaultValue;
                await smartUpdate(context, {
                    fieldType: 'layout',
                    fieldName: 'hero_layout',
                    value: this.value,
                    previousValue: previousValue,
                    page_type: context.pageSelector.value,
                    isGlobal: false
                });
                this.defaultValue = this.value;
            } catch (error) {
                displayError('Failed to update hero layout style');
                this.value = this.defaultValue; // Revert on error
                handleBannerSliderVisibility(this.defaultValue); // Revert visibility
            }
        });
    });

    return true;
}