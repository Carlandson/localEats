import { updateGlobalComponent } from '../components/globalComponents.js';
import { displayError } from '../utils/errors.js';
import { updatePreview } from '../utils/previewUpdates.js';
import { updateHeroText } from './textHandlers.js';

function getFontElements() {
    return {
        mainFontSelect: document.getElementById('main-font'),
        heroHeadingFont: document.getElementById('hero_heading_font'),
        heroSubheadingFont: document.getElementById('hero_subheading_font'),
        heroHeadingSize: document.getElementById('hero_heading_size'),
        heroSubheadingSize: document.getElementById('hero_subheading_size'),
        banner2HeadingFont: document.getElementById('hero_banner_2_heading_font'),
        banner2SubheadingFont: document.getElementById('hero_banner_2_subheading_font'),
        banner2HeadingSize: document.getElementById('hero_banner_2_heading_size'),
        banner2SubheadingSize: document.getElementById('hero_banner_2_subheading_size'),
        banner3HeadingFont: document.getElementById('hero_banner_3_heading_font'),
        banner3SubheadingFont: document.getElementById('hero_banner_3_subheading_font'),
        banner3HeadingSize: document.getElementById('hero_banner_3_heading_size'),
        banner3SubheadingSize: document.getElementById('hero_banner_3_subheading_size')
    };
}

export function initializeFontHandlers(context) {
    console.log('Initializing font handlers');
    
    const elements = getFontElements();

    if (elements.mainFontSelect) {
        console.log('Attaching event listener to main font selector');
        elements.mainFontSelect.addEventListener('change', async function() {
            try {
                console.log('Main font changed to:', this.value);
                await updateGlobalComponent('main_font', this.value, context);
                await updatePreview(context.pageSelector.value, context);
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

    // Get all font and size selectors
    const fontSelectors = document.querySelectorAll('select[id$="_heading_font"], select[id$="_subheading_font"], select[id$="_heading_size"], select[id$="_subheading_size"]');
    
    fontSelectors.forEach(selector => {
        console.log('Found selector:', selector.id);
        
        selector.addEventListener('change', async function() {
            try {
                const idParts = this.id.split('_');
                const isSize = this.id.includes('_size');
                
                // Fix the prefix logic to match field_mapping in views.py
                let prefix;
                if (this.id.includes('banner_2')) {
                    prefix = 'hero_banner_2';  // Changed from 'banner_2'
                } else if (this.id.includes('banner_3')) {
                    prefix = 'hero_banner_3';  // Changed from 'banner_3'
                } else {
                    prefix = 'hero';
                }

                const fieldType = idParts.includes('subheading') ? 
                    (isSize ? 'subheading_size' : 'subheading_font') : 
                    (isSize ? 'heading_size' : 'heading_font');
                const field = `${prefix}_${fieldType}`;
                
                console.log('Font/Size changed:', {
                    element: this.id,
                    field: field,
                    value: this.value,
                    prefix: prefix,
                    fieldType: fieldType
                });

                await updateHeroText(field, this.value, context);
                await updatePreview(context.pageSelector.value, context);
            } catch (error) {
                console.error('Error updating font/size:', error);
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