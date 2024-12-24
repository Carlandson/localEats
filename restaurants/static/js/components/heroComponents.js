import { initializeSlider } from './slider.js';

let sliderInstance = null;
const slider = initializeSlider();

export function handleBannerSliderVisibility(layoutStyle) {
    const bannerSliderContainer = document.getElementById('banner-slider-images');
    if (!bannerSliderContainer) return;
    if (layoutStyle === 'banner-slider') {
        const bannerSliderContainer = document.getElementById('banner-slider-images');
        bannerSliderContainer.style.display = 'block';
        
        // Initialize slider
        if (!sliderInstance) {
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

export function reinitializeSlider() {
    if (sliderInstance) {
        // Store current state
        const slides = sliderContainer.querySelectorAll('.slide');
        console.log(slides.length)
        console.log('ttttttttttttttttttttttttttttttttttttttttttttttttttttttt')
        const currentIndex = sliderInstance.getCurrentSlide();
        const wasPlaying = sliderInstance.isPlaying();
        
        // Stop current instance
        sliderInstance.stop();
        
        // Reinitialize with stored position
        sliderInstance = slider.init(currentIndex);
        
        if (sliderInstance && document.getElementById('banner-slider-images').style.display !== 'none') {
            // Only start if it was playing before
            if (wasPlaying) {
                sliderInstance.start();
            }
        }
    } else {
        console.log('tttttttttttttttttttttttttttttttttttttttttttttttttttttttttt')
        sliderInstance = slider.init(0);
        if (sliderInstance && document.getElementById('banner-slider-images').style.display !== 'none') {
            sliderInstance.start();
        }
    }
}

export function handleBannerButtonVisibility(layoutStyle) {
    const bannerButtonContainer = document.getElementById('banner-button-container');
    if (!bannerButtonContainer) return;
    bannerButtonContainer.style.display = layoutStyle === 'banner-slider' ? 'block' : 'none';
}

