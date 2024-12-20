import { initializeSlider } from './components/slider.js';

let sliderInstance = null;

function initializeComponents() {
    try {
        // Check if we have a slider container and multiple slides
        const sliderContainer = document.querySelector('.slider-container');
        const slides = document.querySelectorAll('.slide');
        
        if (sliderContainer && slides.length > 1) {
            console.log('Initializing slider...');
            const slider = initializeSlider();
            sliderInstance = slider.init();
        }

        // Initialize mobile menu
        const mobileMenuButton = document.querySelector('.mobile-menu-button');
        if (mobileMenuButton) {
            mobileMenuButton.addEventListener('click', () => {
                document.querySelector('.mobile-menu')?.classList.toggle('hidden');
            });
        }

    } catch (error) {
        console.error('Error initializing visitor components:', error);
    }
}

// For preview mode or dynamic content updates
function reinitializeComponents() {
    try {
        // Stop existing slider if it exists
        if (sliderInstance) {
            sliderInstance.stop();
            sliderInstance = null;
        }

        // Reinitialize components
        initializeComponents();
        
    } catch (error) {
        console.error('Error reinitializing visitor components:', error);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initializeComponents);

// Set up observer for preview mode
if (document.querySelector('.preview-mode')) {
    const observer = new MutationObserver(reinitializeComponents);
    const previewContent = document.getElementById('page-content-preview');
    
    if (previewContent) {
        observer.observe(previewContent, {
            childList: true,
            subtree: true
        });
    }
}

