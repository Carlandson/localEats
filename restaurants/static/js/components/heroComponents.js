import { initializeSlider } from './slider.js';

let sliderInstance = null;
const slider = initializeSlider();

export function handleBannerSliderVisibility(layoutStyle) {
    const bannerSliderContainer = document.getElementById('banner-slider-images');
    if (!bannerSliderContainer) return;
    
    console.log('Handling banner slider visibility:', layoutStyle);
    
    if (layoutStyle === 'banner-slider') {
        console.log('Displaying banner slider');
        bannerSliderContainer.style.display = 'block';
        
        // Initialize slider
        if (!sliderInstance) {
            console.log('Initializing slider');
            sliderInstance = slider.init();
            if (sliderInstance) {
                sliderInstance.start();
            }
        }
        
        // Enable banner upload inputs and buttons
        ['banner-2', 'banner-3'].forEach(prefix => {
            const fileInput = document.getElementById(`${prefix}-upload`);
            const uploadButton = document.getElementById(`upload-${prefix}-button`);
            const container = document.getElementById(`${prefix}-container`);
            const removeButton = document.getElementById(`remove-${prefix}`);
            
            if (fileInput) fileInput.disabled = false;
            if (uploadButton) {
                uploadButton.disabled = false;
                uploadButton.classList.remove('opacity-50', 'cursor-not-allowed');
            }
            if (container) container.classList.remove('opacity-50');
            if (removeButton) removeButton.disabled = false;
        });
    } else {
        if (sliderInstance) {
            sliderInstance.stop();
            sliderInstance = null;
        }
        bannerSliderContainer.style.display = 'none';
        
        // Disable banner upload inputs and buttons
        ['banner-2', 'banner-3'].forEach(prefix => {
            const fileInput = document.getElementById(`${prefix}-upload`);
            const uploadButton = document.getElementById(`upload-${prefix}-button`);
            const container = document.getElementById(`${prefix}-container`);
            const removeButton = document.getElementById(`remove-${prefix}`);
            
            if (fileInput) fileInput.disabled = true;
            if (uploadButton) {
                uploadButton.disabled = true;
                uploadButton.classList.add('opacity-50', 'cursor-not-allowed');
            }
            if (container) container.classList.add('opacity-50');
            if (removeButton) removeButton.disabled = true;
        });
    }
}

// Add this function to reinitialize the slider after content changes
export function reinitializeSlider() {
    if (sliderInstance) {
        sliderInstance.stop();
    }
    sliderInstance = slider.init();
    if (sliderInstance && document.getElementById('banner-slider-images').style.display !== 'none') {
        sliderInstance.start();
    }
}