import { displayError } from '../utils/errors.js';
import { smartUpdate } from '../utils/previewUpdates.js';

function getFontElements() {
    return {
        mainFontSelect: document.getElementById('main-font'),
        heroHeadingFont: document.getElementById('hero_heading_font'),
        heroSubheadingFont: document.getElementById('hero_subheading_font'),
        heroHeadingSize: document.getElementById('hero_heading_size'),
        heroSubheadingSize: document.getElementById('hero_subheading_size'),
        banner2HeadingFont: document.getElementById('banner_2_heading_font'),
        banner2SubheadingFont: document.getElementById('banner_2_subheading_font'),
        banner2HeadingSize: document.getElementById('banner_2_heading_size'),
        banner2SubheadingSize: document.getElementById('banner_2_subheading_size'),
        banner3HeadingFont: document.getElementById('banner_3_heading_font'),
        banner3SubheadingFont: document.getElementById('banner_3_subheading_font'),
        banner3HeadingSize: document.getElementById('banner_3_heading_size'),
        banner3SubheadingSize: document.getElementById('banner_3_subheading_size')
    };
}

export function initializeFontHandlers(context) {
    const elements = getFontElements();

    // Handle main font (global setting)
    if (elements.mainFontSelect) {
        elements.mainFontSelect.addEventListener('change', async function() {
            try {
                await smartUpdate(context, {
                    fieldType: 'font',
                    fieldName: 'main_font',
                    value: this.value,
                    previousValue: this.defaultValue,
                    page_type: context.pageSelector.value,
                    return_preview: true,
                    isGlobal: true
                });
                this.defaultValue = this.value;
            } catch (error) {
                console.error('Error updating main font:', error);
                displayError('Failed to update main font');
            }
        });

        // Add preview on hover
        elements.mainFontSelect.addEventListener('mouseover', function(e) {
            if (e.target.tagName === 'OPTION') {
                e.target.style.fontFamily = e.target.value;
            }
        });
    } else {
        console.warn('Main font selector not found');
    }

    // Handle all banner font and size selectors
    const fontSelectors = document.querySelectorAll('select[id$="_heading_font"], select[id$="_subheading_font"], select[id$="_heading_size"], select[id$="_subheading_size"]');
    
    fontSelectors.forEach(selector => {
        selector.addEventListener('change', async function() {
            try {
                const idParts = this.id.split('_');
                const isSize = this.id.includes('_size');
                
                // Get the correct prefix
                let prefix;
                if (this.id.includes('banner_2')) {
                    prefix = 'banner_2';
                } else if (this.id.includes('banner_3')) {
                    prefix = 'banner_3';
                } else {
                    prefix = 'hero';
                }

                const fieldType = idParts.includes('subheading') ? 
                    (isSize ? 'subheading_size' : 'subheading_font') : 
                    (isSize ? 'heading_size' : 'heading_font');
                
                const fieldName = `${prefix}_${fieldType}`;
                
                await smartUpdate(context, {
                    fieldType: isSize ? 'size' : 'font',
                    fieldName: fieldName,
                    value: this.value,
                    previousValue: this.defaultValue,
                    page_type: context.pageSelector.value,
                    return_preview: true,
                    isGlobal: false
                });
                
                // Update the defaultValue for future changes
                this.defaultValue = this.value;
                
            } catch (error) {
                console.error(`Error updating ${this.id}:`, error);
                displayError(`Failed to update ${this.id.includes('size') ? 'size' : 'font'}`);
            }
        });

        // Add preview on hover for font selectors only
        if (selector.id.includes('_font')) {
            selector.addEventListener('mouseover', function(e) {
                if (e.target.tagName === 'OPTION') {
                    e.target.style.fontFamily = e.target.value;
                }
            });
        }
    });
}