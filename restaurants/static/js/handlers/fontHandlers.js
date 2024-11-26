import { updateGlobalComponent } from '../components/globalComponents.js';
import { displayError } from '../utils/errors.js';
import { updatePreview } from '../utils/previewUpdates.js';

function getFontElements() {
    return {
        mainFontSelect: document.getElementById('main-font'),
        heroHeadingFont: document.getElementById('hero-heading-font'),
        heroSubheadingFont: document.getElementById('hero-subheading-font'),
        heroHeadingSize: document.getElementById('hero-heading-size'),
        heroSubheadingSize: document.getElementById('hero-subheading-size'),
        bannerTwoHeadingSize: document.getElementById('banner-2-heading-size'),
        bannerTwoSubheadingSize: document.getElementById('banner-2-subheading-size'),
        bannerThreeHeadingSize: document.getElementById('banner-3-heading-size'),
        bannerThreeSubheadingSize: document.getElementById('banner-3-subheading-size')
    };
}

export function initializeFontHandlers(context) {
    const elements = getFontElements();

    // Initialize main font selector
    if (elements.mainFontSelect) {
        elements.mainFontSelect.addEventListener('change', async function () {
            try {
                await updateGlobalComponent('main_font', this.value, context);
                await updatePreview(context.pageSelector.value, context);
            } catch (error) {
                console.error('Error updating main font:', error);
                displayError('Failed to update main font');
            }
        });

        // Add preview on hover
        elements.mainFontSelect.addEventListener('mouseover', function (e) {
            if (e.target.tagName === 'OPTION') {
                e.target.style.fontFamily = e.target.value;
            }
        });
    }

    // Initialize hero heading font
    if (elements.heroHeadingFont) {
        elements.heroHeadingFont.addEventListener('change', async function () {
            try {
                await updateGlobalComponent('hero_heading_font', this.value, context);
                await updatePreview(context.pageSelector.value, context);
            } catch (error) {
                console.error('Error updating heading font:', error);
                displayError('Failed to update heading font');
            }
        });
    }

    // Initialize hero subheading font
    if (elements.heroSubheadingFont) {
        elements.heroSubheadingFont.addEventListener('change', async function () {
            try {
                await updateGlobalComponent('hero_subheading_font', this.value, context);
                await updatePreview(context.pageSelector.value, context);
            } catch (error) {
                console.error('Error updating subheading font:', error);
                displayError('Failed to update subheading font');
            }
        });
    }

    // Initialize font size selectors
    const sizeSelectors = {
        [elements.heroHeadingSize?.id]: 'hero_heading_size',
        [elements.heroSubheadingSize?.id]: 'hero_subheading_size'
    };

    Object.entries(sizeSelectors).forEach(([elementId, componentName]) => {
        const element = document.getElementById(elementId);
        if (element) {
            element.addEventListener('change', async function () {
                try {
                    await updateGlobalComponent(componentName, this.value, context);
                    await updatePreview(context.pageSelector.value, context);
                } catch (error) {
                    console.error(`Error updating ${componentName}:`, error);
                    displayError(`Failed to update ${componentName.replace('_', ' ')}`);
                }
            });
        }
    });
}